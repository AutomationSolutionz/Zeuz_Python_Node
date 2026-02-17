import subprocess
import time
import sys
import threading
import json
import re
import os
from pathlib import Path
import shutil
from datetime import datetime, timedelta

def run_nmap(ip, output_dir=None):
    os.makedirs(output_dir, exist_ok=True)
    xml_output_file = os.path.join(output_dir, f"nmap_scan_{ip}.xml")
    normal_output_file = os.path.join(output_dir, f"nmap_scan_{ip}.txt")

    process = subprocess.Popen(["nmap", "-sV", "--script", "vuln", "-oX", xml_output_file, "-oN", normal_output_file, ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    spinner = ['|', '/', '-', '\\']
    start_time = datetime.now()
    scanning = True
    def show_progress():
        i = 0
        while scanning:
            elapsed = datetime.now() - start_time
            elapsed_str = str(timedelta(seconds=int(elapsed.total_seconds())))
            sys.stdout.write(f"\rScanning {ip} {spinner[i]} [Running for: {elapsed_str}]")
            sys.stdout.flush()
            i = (i + 1) % 4
            time.sleep(0.25)
    progress_thread = threading.Thread(target=show_progress)
    progress_thread.start()
    process.wait()
    scanning = False
    progress_thread.join()
    total_time = datetime.now() - start_time
    total_time_str = str(timedelta(seconds=int(total_time.total_seconds())))
    print(f"\rScan completed in {total_time_str}" + " " * 30)
    return xml_output_file, normal_output_file

def parse_nmap_output(xml_file):
    from xml.etree import ElementTree as ET
    tree = ET.parse(xml_file)
    root = tree.getroot()
    vulnerabilities = []
    nmaprun = root.attrib
    start_time = datetime.fromtimestamp(int(nmaprun.get("start", 0))).strftime("%Y-%m-%d %H:%M:%S")
    
    finished = root.find("runstats/finished")
    end_time = datetime.fromtimestamp(int(finished.get("time", 0))).strftime("%Y-%m-%d %H:%M:%S") if finished is not None else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    scan_info = {
        "scan_time": end_time,
        "start_time": start_time,
        "end_time": end_time,
        "total_hosts": root.find("runstats/hosts").get("total") if root.find("runstats/hosts") is not None else "Unknown",
        "up_hosts": root.find("runstats/hosts").get("up") if root.find("runstats/hosts") is not None else "Unknown",
        "scan_type": nmaprun.get("scanner", "Nmap") + " " + nmaprun.get("version", ""),
        "arguments": nmaprun.get("args", "")
    }
    network_info = []

    for host in root.findall('host'):
        ip_address = host.find("address").get("addr")
        for address in host.findall("address"):
            addr_type = address.get("addrtype")
            addr = address.get("addr")
            vendor = address.get("vendor", "Unknown")
            
            network_info.append({
                "type": addr_type,
                "address": addr,
                "vendor": vendor
            })
        
        hostname_elem = host.find("hostnames/hostname")
        hostname = hostname_elem.get("name") if hostname_elem is not None else "Unknown"
        
        if hostname != "Unknown":
            network_info.append({
                "type": "hostname",
                "address": hostname,
                "vendor": "DNS"
            })

        for port in host.findall("ports/port"):
            port_id = port.get("portid")
            protocol = port.get("protocol")
            state_elem = port.find("state")
            state = state_elem.get("state") if state_elem is not None else "Unknown"
            
            service_elem = port.find("service")
            service = service_elem.get("name") if service_elem is not None else "Unknown"
            product = service_elem.get("product") if service_elem is not None else ""
            version = service_elem.get("version") if service_elem is not None else ""
            
            service_info = f"{service}"
            if product:
                service_info += f" ({product}"
                if version:
                    service_info += f" {version}"
                service_info += ")"
            
            network_info.append({
                "type": f"service ({port_id}/{protocol})",
                "address": service,
                "vendor": f"{product} {version}".strip()
            })

            for script in port.findall("script"):
                script_id = script.get("id")
                script_output = script.get("output")

                if "CVE" in script_output or "EXPLOIT" in script_output:
                    cve_matches = re.findall(r'(CVE-\d{4}-\d+)', script_output)
                    severity_matches = re.findall(r'(\d\.\d)', script_output)
                    description_match = re.search(r'VULNERABLE:\s*(.*?)(?=\n\n|\n\s*\|\s*|\Z)', script_output, re.DOTALL)
                    description = description_match.group(1).strip() if description_match else "No description available"

                    for i in range(len(cve_matches)):
                        vulnerabilities.append({
                            "ip": ip_address,
                            "hostname": hostname,
                            "port": port_id,
                            "protocol": protocol,
                            "state": state,
                            "service": service_info,
                            "script": script_id,
                            "cve": cve_matches[i],
                            "severity": float(severity_matches[i]) if i < len(severity_matches) else 0,
                            "description": description
                        })
    
    scan_info["network_info"] = network_info

    return vulnerabilities, scan_info

def generate_html(vulnerabilities, scan_info, target_ip, output_dir=None):
    """Generate HTML report for security vulnerabilities."""
    
    severity_counts = {
        "Critical (8.0-10.0)": 0,
        "High (6.0-7.9)": 0,
        "Medium (4.0-5.9)": 0,
        "Low (0.1-3.9)": 0,
        "None (0.0)": 0
    }
    
    for v in vulnerabilities:
        if v["severity"] >= 8.0:
            severity_counts["Critical (8.0-10.0)"] += 1
        elif v["severity"] >= 6.0:
            severity_counts["High (6.0-7.9)"] += 1
        elif v["severity"] >= 4.0:
            severity_counts["Medium (4.0-5.9)"] += 1
        elif v["severity"] > 0:
            severity_counts["Low (0.1-3.9)"] += 1
        else:
            severity_counts["None (0.0)"] += 1
    
    severity_data = [{"level": k, "count": v} for k, v in severity_counts.items()]
    json_severity_data = json.dumps(severity_data)
    
    chart_data = [{"cve": v["cve"], "severity": v["severity"]} for v in vulnerabilities]
    json_data = json.dumps(chart_data)
    
    service_counts = {}
    for v in vulnerabilities:
        service_name = v["service"].split(" ")[0]
        service_counts[service_name] = service_counts.get(service_name, 0) + 1
    service_data = [{"service": k, "count": v} for k, v in service_counts.items()]
    json_service_data = json.dumps(service_data)
    
    port_counts = {}
    for v in vulnerabilities:
        port_counts[v["port"]] = port_counts.get(v["port"], 0) + 1
    port_data = [{"port": k, "count": v} for k, v in port_counts.items()]
    json_port_data = json.dumps(port_data)
    
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scan_date = scan_info.get("scan_time", current_datetime)
    
    # Calculate scan duration if available
    scan_duration = "N/A"
    if "start_time" in scan_info and "end_time" in scan_info:
        start_time = datetime.strptime(scan_info["start_time"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(scan_info["end_time"], "%Y-%m-%d %H:%M:%S")
        duration = end_time - start_time
        scan_duration = f"{duration.seconds // 60} minutes, {duration.seconds % 60} seconds"
    
    # Calculate risk score (fixed to be between 0-100)
    total_severity = sum(v["severity"] for v in vulnerabilities)
    vuln_count = len(vulnerabilities)
    
    if vuln_count > 0:
        # Base score on average severity and number of vulnerabilities
        avg_severity = total_severity / vuln_count
        # Scale from 0-10 to 0-70 (severity component)
        severity_component = (avg_severity / 10) * 70
        # Scale count component (max out at 20 vulnerabilities)
        count_component = min(vuln_count / 20, 1) * 30
        risk_score = round(severity_component + count_component)
        # Ensure score is capped at 100
        risk_score = min(risk_score, 100)
    else:
        risk_score = 0
    
    network_info_rows = ""
    for info in scan_info.get("network_info", []):
        network_info_rows += f"""
        <tr>
            <td>{info['type']}</td>
            <td>{info['address']}</td>
            <td>{info['vendor']}</td>
        </tr>
        """
    table_rows = ""
    for v in sorted(vulnerabilities, key=lambda x: x['severity'], reverse=True):
        if v['severity'] >= 8.0:
            severity_class = "critical"
        elif v['severity'] >= 6.0:
            severity_class = "high"
        elif v['severity'] >= 4.0:
            severity_class = "medium"
        elif v['severity'] > 0:
            severity_class = "low"
        else:
            severity_class = "none"
            
        table_rows += f"""
        <tr>
            <td>{v['ip']}</td>
            <td>{v['hostname']}</td>
            <td>{v['port']}/{v['protocol']}</td>
            <td>{v['service']}</td>
            <td><a href="https://nvd.nist.gov/vuln/detail/{v['cve']}" target="_blank">{v['cve']}</a></td>
            <td>
                <span class="severity-badge {severity_class}">
                    {v['severity']}
                </span>
            </td>
            <td class="description">{v['description']}</td>
        </tr>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Vulnerability Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                margin-bottom: 20px;
            }}
            
            .summary-box {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
            }}
            
            .summary-card {{
                flex: 1;
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                margin: 0 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            
            .card {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            
            .dashboard {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                flex: 1;
                min-width: 300px;
                height: 300px;
                position: relative;
            }}
            
            /* Fixed height container for threat chart */
            .threat-chart-container {{
                height: 300px;
                width: 100%;
                position: relative;
            }}
            
            h1 {{
                color: white;
                margin: 0;
            }}
            
            h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            
            h3 {{
                color: #2c3e50;
                margin-top: 0;
            }}
            
            .scan-info {{
                margin-bottom: 20px;
                font-size: 0.9em;
                color: #777;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            
            th {{
                background-color: #2c3e50;
                color: white;
                position: sticky;
                top: 0;
            }}
            
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            
            tr:hover {{
                background-color: #f1f1f1;
            }}
            
            .severity-badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }}
            
            .critical {{
                background-color: #d9534f;
            }}
            
            .high {{
                background-color: #f0ad4e;
            }}
            
            .medium {{
                background-color: #5bc0de;
            }}
            
            .low {{
                background-color: #5cb85c;
            }}
            
            .none {{
                background-color: #777;
            }}
            
            .risk-meter {{
                height: 30px;
                background: linear-gradient(to right, #5cb85c, #f0ad4e, #d9534f);
                border-radius: 15px;
                margin: 10px 0;
                position: relative;
            }}
            
            .risk-indicator {{
                position: absolute;
                top: -10px;
                width: 10px;
                height: 50px;
                background-color: #333;
                border-radius: 5px;
            }}
            
            footer {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                font-size: 0.9em;
                color: #777;
                border-top: 1px solid #eee;
            }}
            
            .description {{
                max-width: 300px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            
            .description:hover {{
                white-space: normal;
                word-wrap: break-word;
            }}
            
            @media print {{
                body {{
                    background-color: white;
                }}
                .card, .summary-card {{
                    box-shadow: none;
                    border: 1px solid #ddd;
                }}
                .header {{
                    background-color: #eee;
                    color: black;
                }}
                th {{
                    background-color: #eee;
                    color: black;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Security Vulnerability Report</h1>
                <p>Target: {target_ip}</p>
            </div>
            
            <div class="scan-info">
                <strong>Scan Date:</strong> {scan_date} | 
                <strong>Scan Duration:</strong> {scan_duration} | 
                <strong>Total Hosts Scanned:</strong> {scan_info.get("total_hosts", "N/A")} | 
                <strong>Hosts Up:</strong> {scan_info.get("up_hosts", "N/A")} | 
                <strong>Report Generated:</strong> {current_datetime}
            </div>

            <div class="card">
                <h2>Network Information</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Address</th>
                        <th>Vendor/Info</th>
                    </tr>
                    {network_info_rows}
                </table>
            </div>

            <div class="summary-box">
                <div class="summary-card">
                    <h3>Total Vulnerabilities</h3>
                    <p style="font-size: 24px; font-weight: bold;">{len(vulnerabilities)}</p>
                </div>
                <div class="summary-card">
                    <h3>Risk Score</h3>
                    <p style="font-size: 24px; font-weight: bold;">{risk_score}/100</p>
                    <div class="risk-meter">
                        <div class="risk-indicator" style="left: calc({risk_score}% - 5px);"></div>
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Critical Vulnerabilities</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #d9534f;">{severity_counts["Critical (8.0-10.0)"]}</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Vulnerability Overview</h2>
                <div class="dashboard">
                    <div class="chart-container">
                        <canvas id="severityDistChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="serviceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="portChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Top Vulnerabilities by Severity</h2>
                <div class="threat-chart-container">
                    <canvas id="threatChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>Vulnerability Details</h2>
                <div style="overflow-x: auto;">
                    <table>
                        <tr>
                            <th>IP Address</th>
                            <th>Hostname</th>
                            <th>Port/Protocol</th>
                            <th>Service</th>
                            <th>CVE</th>
                            <th>Severity</th>
                            <th>Description</th>
                        </tr>
                        {table_rows}
                    </table>
                </div>
            </div>
            
            <footer>
                <p>This report was automatically generated and provides a summary of potential security vulnerabilities. 
                All findings should be verified by a security professional.</p>
            </footer>
        </div>

        <script>
            // Sort vulnerabilities by severity for the bar chart
            const threatData = {json_data};
            threatData.sort((a, b) => b.severity - a.severity);
            const topThreats = threatData.slice(0, 10); // Top 10 vulnerabilities
            
            // Charts data
            const serviceData = {json_service_data};
            const portData = {json_port_data};
            const severityDistData = {json_severity_data};
            
            // Severity Distribution Chart
            new Chart(document.getElementById('severityDistChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: severityDistData.map(d => d.level),
                    datasets: [{{
                        label: 'Number of Vulnerabilities',
                        data: severityDistData.map(d => d.count),
                        backgroundColor: [
                            'rgba(217, 83, 79, 0.7)',  // Critical
                            'rgba(240, 173, 78, 0.7)', // High
                            'rgba(91, 192, 222, 0.7)', // Medium
                            'rgba(92, 184, 92, 0.7)',  // Low
                            'rgba(119, 119, 119, 0.7)' // None
                        ],
                        borderColor: [
                            'rgb(217, 83, 79)',
                            'rgb(240, 173, 78)',
                            'rgb(91, 192, 222)',
                            'rgb(92, 184, 92)',
                            'rgb(119, 119, 119)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Vulnerabilities by Severity'
                        }},
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                precision: 0
                            }}
                        }}
                    }}
                }}
            }});

            // Service Distribution Pie Chart
            new Chart(document.getElementById('serviceChart').getContext('2d'), {{
                type: 'pie',
                data: {{
                    labels: serviceData.map(d => d.service),
                    datasets: [{{
                        data: serviceData.map(d => d.count),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Vulnerabilities by Service'
                        }}
                    }}
                }}
            }});
            
            // Port Distribution Pie Chart
            new Chart(document.getElementById('portChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: portData.map(d => 'Port ' + d.port),
                    datasets: [{{
                        data: portData.map(d => d.count),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Vulnerabilities by Port'
                        }}
                    }}
                }}
            }});

            // Top Vulnerabilities Bar Chart - Fixed height
            new Chart(document.getElementById('threatChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: topThreats.map(d => d.cve),
                    datasets: [{{
                        label: 'Severity Score',
                        data: topThreats.map(d => d.severity),
                        backgroundColor: topThreats.map(d => 
                            d.severity >= 8.0 ? 'rgba(217, 83, 79, 0.7)' :
                            d.severity >= 6.0 ? 'rgba(240, 173, 78, 0.7)' :
                            d.severity >= 4.0 ? 'rgba(91, 192, 222, 0.7)' :
                            'rgba(92, 184, 92, 0.7)'
                        ),
                        borderColor: topThreats.map(d => 
                            d.severity >= 8.0 ? 'rgb(217, 83, 79)' :
                            d.severity >= 6.0 ? 'rgb(240, 173, 78)' :
                            d.severity >= 4.0 ? 'rgb(91, 192, 222)' :
                            'rgb(92, 184, 92)'
                        ),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {{
                        duration: 0 // Disable animations
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Top Vulnerabilities by Severity'
                        }},
                        legend: {{
                            display: false
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 10,
                            right: 10,
                            bottom: 10,
                            left: 10
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 10, // Fixed max value
                            title: {{
                                display: true,
                                text: 'Severity Score (0-10)'
                            }},
                            ticks: {{
                                stepSize: 2 // Fixed step size
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'CVE ID'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    output_file = os.path.join(output_dir, f"security_report_{target_ip}.html")
    with open(output_file, "w") as f:
        f.write(html_template)

    print(f"Enhanced security report saved: {output_file}")
    return output_file


def nmap_scan_run(url, security_report_dir=None):
    ip_address = url
    security_report_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving all reports directly to: {security_report_dir}")
    print("Running Nmap scan. It may take a while...")
    xml_result, text_result = run_nmap(ip_address, security_report_dir)
    print(f"Scan complete! Results saved to:")
    print(f"- XML format: {xml_result}")
    print(f"- Terminal format: {text_result}")
    
    print("Parsing results...")
    vuln_data, scan_info = parse_nmap_output(xml_result)
    
    print("Generating HTML report...")
    html_result = generate_html(vuln_data, scan_info, ip_address, security_report_dir)
    
    return {
        "xml": xml_result,
        "txt": text_result,
        "html": html_result
    }