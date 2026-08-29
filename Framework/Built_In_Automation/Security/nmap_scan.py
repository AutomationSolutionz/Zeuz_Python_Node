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
import socket
import ssl
import urllib.request
import urllib.parse

def run_nmap(ip, output_dir=None):
    os.makedirs(output_dir, exist_ok=True)
    xml_output_file = os.path.join(output_dir, f"nmap_scan_{ip}.xml")
    normal_output_file = os.path.join(output_dir, f"nmap_scan_{ip}.txt")

    process = subprocess.Popen(["nmap", "-sV", "-T4", "--open", "--min-rate", "1000", "--script", "vuln", "-oX", xml_output_file, "-oN", normal_output_file, ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

                # Check for vulnerability indicators
                is_vulnerable = "VULNERABLE" in script_output or "CVE" in script_output or "EXPLOIT" in script_output or "vulnerable" in script_output.lower()
                
                if is_vulnerable:
                    cve_matches = re.findall(r'(CVE-\d{4}-\d+)', script_output)
                    severity_matches = re.findall(r'(\d\.\d)', script_output)
                    
                    # Extract description
                    description_match = re.search(r'VULNERABLE:\s*(.*?)(?=\n\n|\n\s*\|\s*|\Z)', script_output, re.DOTALL)
                    if not description_match:
                         # Fallback to just the output if regex fails
                         description = script_output[:200] + "..." if len(script_output) > 200 else script_output
                    else:
                        description = description_match.group(1).strip()

                    # Logic to handle cases with CVEs and without
                    if cve_matches:
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
                                "severity": float(severity_matches[i]) if i < len(severity_matches) else 5.0, # Default to medium if severity not found
                                "description": description
                            })
                    else:
                        # No CVE found but it is a vulnerability
                        vulnerabilities.append({
                            "ip": ip_address,
                            "hostname": hostname,
                            "port": port_id,
                            "protocol": protocol,
                            "state": state,
                            "service": service_info,
                            "script": script_id,
                            "cve": "N/A",
                            "severity": 5.0, # Default risk for unknown vulnerabilities
                            "description": description
                        })
    
    scan_info["network_info"] = network_info

    return vulnerabilities, scan_info

def generate_html(vulnerabilities, scan_info, target_ip, output_dir=None, crypto_data=None):
    """Generate HTML report for security vulnerabilities."""
    
    severity_counts = {
        "Critical (8.0-10.0)": 0,
        "High (6.0-7.9)": 0,
        "Medium (4.0-5.9)": 0,
        "Low (0.1-3.9)": 0,
        "None (0.0)": 0
    }
    
    # Calculate Severity Counts
    for v in vulnerabilities:
        # Ensure severity is a float
        try:
            sev = float(v.get("severity", 0))
        except (ValueError, TypeError):
            sev = 0.0
            
        if sev >= 8.0:
            severity_counts["Critical (8.0-10.0)"] += 1
        elif sev >= 6.0:
            severity_counts["High (6.0-7.9)"] += 1
        elif sev >= 4.0:
            severity_counts["Medium (4.0-5.9)"] += 1
        elif sev > 0:
            severity_counts["Low (0.1-3.9)"] += 1
        else:
            severity_counts["None (0.0)"] += 1
    
    # JSON Data for Charts
    severity_data = [{"level": k, "count": v} for k, v in severity_counts.items()]
    json_severity_data = json.dumps(severity_data)
    
    chart_data = [{"cve": v.get("cve", "N/A"), "severity": v.get("severity", 0)} for v in vulnerabilities]
    json_data = json.dumps(chart_data)
    
    service_counts = {}
    for v in vulnerabilities:
        service_name = v.get("service", "Unknown").split(" ")[0]
        service_counts[service_name] = service_counts.get(service_name, 0) + 1
    service_data = [{"service": k, "count": v} for k, v in service_counts.items()]
    json_service_data = json.dumps(service_data)
    
    port_counts = {}
    for v in vulnerabilities:
        port_val = v.get("port", "Unknown")
        port_counts[port_val] = port_counts.get(port_val, 0) + 1
    port_data = [{"port": k, "count": v} for k, v in port_counts.items()]
    json_port_data = json.dumps(port_data)
    
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scan_date = scan_info.get("scan_time", current_datetime)
    
    # Calculate scan duration if available
    scan_duration = "N/A"
    if "start_time" in scan_info and "end_time" in scan_info:
        try:
            start_time = datetime.strptime(scan_info["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(scan_info["end_time"], "%Y-%m-%d %H:%M:%S")
            duration = end_time - start_time
            scan_duration = f"{duration.seconds // 60}m {duration.seconds % 60}s"
        except Exception:
            pass
    
    # Calculate risk score (0-100)
    vuln_count = len(vulnerabilities)
    is_clean = vuln_count == 0
    
    risk_score = 0
    risk_level = "Secure"
    risk_color = "#10b981" # Green
    
    if not is_clean:
        total_severity = sum(float(v.get("severity", 0)) for v in vulnerabilities)
        avg_severity = total_severity / vuln_count
        severity_component = (avg_severity / 10) * 70
        count_component = min(vuln_count / 20, 1) * 30
        risk_score = round(severity_component + count_component)
        risk_score = min(risk_score, 100)
        
        if risk_score >= 80:
            risk_level = "Critical"
            risk_color = "#dc3545"
        elif risk_score >= 60:
            risk_level = "High"
            risk_color = "#f59e0b"
        elif risk_score >= 40:
            risk_level = "Medium"
            risk_color = "#3b82f6"
        else:
            risk_level = "Low"
            risk_color = "#10b981"
            
    # Network Info Rows
    network_info_rows = ""
    for info in scan_info.get("network_info", []):
        network_info_rows += f"""
        <tr>
            <td><span class="badge badge-secondary">{info.get('type', 'Unknown')}</span></td>
            <td class="font-mono">{info.get('address', 'N/A')}</td>
            <td>{info.get('vendor', '')}</td>
        </tr>
        """
        
    # Vulnerability Table Rows
    table_rows = ""
    sorted_vulns = sorted(vulnerabilities, key=lambda x: float(x.get('severity', 0)), reverse=True)
    
    for v in sorted_vulns:
        sev = float(v.get('severity', 0))
        if sev >= 8.0:
            severity_class = "severity-critical"
            sev_label = "CRITICAL"
        elif sev >= 6.0:
            severity_class = "severity-high"
            sev_label = "HIGH"
        elif sev >= 4.0:
            severity_class = "severity-medium"
            sev_label = "MEDIUM"
        elif sev > 0:
            severity_class = "severity-low"
            sev_label = "LOW"
        else:
            severity_class = "severity-none"
            sev_label = "INFO"
            
        cve_display = v.get('cve', 'N/A')
        cve_link = f'<a href="https://nvd.nist.gov/vuln/detail/{cve_display}" target="_blank" class="cve-link">{cve_display}</a>' if cve_display != "N/A" else "N/A"
            
        table_rows += f"""
        <tr>
            <td class="text-center"><span class="severity-badge {severity_class}">{sev}</span></td>
            <td>
                <div class="service-name">{v.get('service', 'Unknown')}</div>
                <div class="port-info">{v.get('port', 'N/A')}/{v.get('protocol', 'tcp')}</div>
            </td>
            <td>{cve_link}</td>
            <td>
                <div class="vuln-description">{v.get('description', 'No description')}</div>
                <div class="vuln-meta">Script: {v.get('script', 'Unknown')}</div>
            </td>
        </tr>
        """

    # HTML Template Construction
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Scan Report - {target_ip}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{
                --primary: #2563eb;
                --secondary: #64748b;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --dark: #0f172a;
                --light: #f8fafc;
                --surface: #ffffff;
                --border: #e2e8f0;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f1f5f9;
                color: #334155;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            /* Header */
            .header {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                color: white;
                padding: 40px 0;
                margin-bottom: -60px;
                padding-bottom: 80px;
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .logo h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
            .logo p {{ margin: 5px 0 0; opacity: 0.8; font-size: 14px; }}
            
            .scan-meta {{
                text-align: right;
                font-size: 13px;
                opacity: 0.9;
            }}
            
            /* Cards */
            .card {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                padding: 24px;
                margin-bottom: 24px;
                border: 1px solid var(--border);
            }}
            
            .section-title {{
                font-size: 18px;
                font-weight: 600;
                color: var(--dark);
                margin-top: 0;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            /* Status Hero */
            .status-hero {{
                text-align: center;
                padding: 40px;
                position: relative;
                overflow: hidden;
            }}
            
            .status-icon {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                font-size: 40px;
            }}
            
            .status-icon.secure {{ background: #d1fae5; color: #059669; }}
            .status-icon.danger {{ background: #fee2e2; color: #b91c1c; }}
            
            .status-title {{ font-size: 28px; font-weight: 700; margin-bottom: 10px; color: var(--dark); }}
            .status-desc {{ color: var(--secondary); max-width: 600px; margin: 0 auto; }}
            
            /* Stats Grid */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 24px;
            }}
            
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid var(--border);
                text-align: center;
            }}
            
            .stat-value {{ font-size: 32px; font-weight: 700; color: var(--dark); }}
            .stat-label {{ font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; color: var(--secondary); margin-top: 5px; }}
            
            /* Tables */
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 12px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--secondary); background: #f8fafc; border-bottom: 1px solid var(--border); }}
            td {{ padding: 16px; border-bottom: 1px solid var(--border); font-size: 14px; vertical-align: top; }}
            tr:last-child td {{ border-bottom: none; }}
            
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
            .badge-secondary {{ background: #e2e8f0; color: #475569; }}
            
            .font-mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }}
            
            /* Vulnerability Styles */
            .severity-badge {{ 
                display: inline-block; 
                width: 36px; 
                height: 36px; 
                line-height: 36px; 
                text-align: center; 
                border-radius: 8px; 
                color: white; 
                font-weight: 700; 
                font-size: 14px;
            }}
            .severity-critical {{ background-color: var(--danger); }}
            .severity-high {{ background-color: var(--warning); }}
            .severity-medium {{ background-color: #3b82f6; }}
            .severity-low {{ background-color: var(--success); }}
            .severity-none {{ background-color: var(--secondary); }}
            
            .service-name {{ font-weight: 600; color: var(--dark); }}
            .port-info {{ font-size: 12px; color: var(--secondary); margin-top: 2px; }}
            
            .cve-link {{ color: var(--primary); text-decoration: none; font-weight: 500; }}
            .cve-link:hover {{ text-decoration: underline; }}
            
            .vuln-description {{ color: #334155; margin-bottom: 4px; }}
            .vuln-meta {{ font-size: 12px; color: #94a3b8; }}
            
            /* Charts */
            .charts-row {{
                display: flex;
                gap: 24px;
                margin-bottom: 24px;
                flex-wrap: wrap;
            }}
            
            .chart-box {{ flex: 1; min-width: 300px; height: 300px; position: relative; }}
            
            .text-center {{ text-align: center; }}
            
            footer {{
                text-align: center;
                padding: 40px;
                color: var(--secondary);
                font-size: 13px;
            }}
        </style>
    </head>
    
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <h1>Security Scan Report</h1>
                    <p>Target: {target_ip}</p>
                </div>
                <div class="scan-meta">
                    <div>{scan_date}</div>
                    <div>Duration: {scan_duration}</div>
                </div>
            </div>
        </div>
        
        <div class="container">
            <!-- Hero Status Section -->
            <div class="card status-hero">
                {'<div class="status-icon secure">✓</div>' if is_clean else f'<div class="status-icon danger" style="background-color: {risk_color}20; color: {risk_color}">!</div>'}
                <div class="status-title">
                    {'No Security Risks Found' if is_clean else f'{vuln_count} Security Risks Detected'}
                </div>
                <div class="status-desc">
                    {'Great job! No known vulnerabilities were detected on the target system.' if is_clean else f'The scan identified potential vulnerabilities with a Risk Score of {risk_score}/100. Immediate attention is recommended for Critical and High severity issues.'}
                </div>
            </div>
            
            {'<!-- Vulnerability Stats -->' if not is_clean else ''}
            {f'''
            <div class="stats-grid">
                <div class="stat-card" style="border-top: 4px solid var(--danger);">
                    <div class="stat-value" style="color: var(--danger)">{severity_counts["Critical (8.0-10.0)"]}</div>
                    <div class="stat-label">Critical</div>
                </div>
                <div class="stat-card" style="border-top: 4px solid var(--warning);">
                    <div class="stat-value" style="color: var(--warning)">{severity_counts["High (6.0-7.9)"]}</div>
                    <div class="stat-label">High</div>
                </div>
                <div class="stat-card" style="border-top: 4px solid #3b82f6;">
                    <div class="stat-value" style="color: #3b82f6">{severity_counts["Medium (4.0-5.9)"]}</div>
                    <div class="stat-label">Medium</div>
                </div>
                <div class="stat-card" style="border-top: 4px solid var(--success);">
                    <div class="stat-value" style="color: var(--success)">{severity_counts["Low (0.1-3.9)"]}</div>
                    <div class="stat-label">Low</div>
                </div>
            </div>
            
            <div class="card">
                <div class="section-title">Vulnerability Analysis</div>
                <div class="charts-row">
                    <div class="chart-box">
                        <canvas id="severityChart"></canvas>
                    </div>
                    <div class="chart-box">
                        <canvas id="serviceChart"></canvas>
                    </div>
                </div>
            </div>
            ''' if not is_clean else ''}
            
            <!-- Network Information -->
            <div class="card">
                <div class="section-title">Network Information</div>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Address</th>
                            <th>Vendor / Info</th>
                        </tr>
                    </thead>
                    <tbody>
                        {network_info_rows}
                    </tbody>
                </table>
            </div>
            
            {'<!-- Detailed Findings -->' if not is_clean else ''}
            {f'''
            <div class="card">
                <div class="section-title">Detailed Findings</div>
                <table>
                    <thead>
                        <tr>
                            <th class="text-center" width="60">Sev</th>
                            <th width="20%">Service</th>
                            <th width="15%">CVE</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            ''' if not is_clean else ''}
            
            {get_crypto_html_snippets(crypto_data) if crypto_data else ''}
            
            <footer>
                <p>Generated by Zeuz Security Automation Framework &bull; {current_datetime}</p>
            </footer>
        </div>
        
        <script>
            // Only render charts if we have data
            if ({'true' if not is_clean else 'false'}) {{
                const severityCtx = document.getElementById('severityChart').getContext('2d');
                new Chart(severityCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
                        datasets: [{{
                            label: 'Vulnerabilities',
                            data: [
                                {severity_counts["Critical (8.0-10.0)"]}, 
                                {severity_counts["High (6.0-7.9)"]}, 
                                {severity_counts["Medium (4.0-5.9)"]}, 
                                {severity_counts["Low (0.1-3.9)"]},
                                {severity_counts["None (0.0)"]}
                            ],
                            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#94a3b8'],
                            borderRadius: 6
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }},
                            title: {{ display: true, text: 'Severity Distribution' }}
                        }},
                        scales: {{
                            y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
                        }}
                    }}
                }});
                
                // Service Chart
                const serviceData = {json_service_data};
                const serviceCtx = document.getElementById('serviceChart').getContext('2d');
                new Chart(serviceCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: serviceData.map(d => d.service),
                        datasets: [{{
                            data: serviceData.map(d => d.count),
                            backgroundColor: [
                                '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
                                '#8b5cf6', '#ec4899', '#64748b'
                            ],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ position: 'right' }},
                            title: {{ display: true, text: 'Affected Services' }}
                        }}
                    }}
                }});
            }}
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
    if hasattr(security_report_dir, 'mkdir'):
        security_report_dir.mkdir(parents=True, exist_ok=True)
    elif security_report_dir:
        os.makedirs(security_report_dir, exist_ok=True)
        
    print(f"Saving all reports directly to: {security_report_dir}")
    print("Running Nmap scan. It may take a while...")
    xml_result, text_result = run_nmap(ip_address, security_report_dir)
    print(f"Scan complete! Results saved to:")
    print(f"- XML format: {xml_result}")
    print(f"- Terminal format: {text_result}")
    
    print("Parsing results...")
    vuln_data, scan_info = parse_nmap_output(xml_result)
    
    print("Running Cryptography & Surface Level scan (Background)...")
    crypto_data = get_cryptography_data(ip_address)
    
    print("Generating HTML report...")
    html_result = generate_html(vuln_data, scan_info, ip_address, security_report_dir, crypto_data)
    
    return {
        "xml": xml_result,
        "txt": text_result,
        "html": html_result,
        "crypto": crypto_data
    }

def get_crypto_html_snippets(crypto_data):
    ssl_info = crypto_data.get('ssl', {})
    headers_info = crypto_data.get('headers', {})
    banner_info = crypto_data.get('banner', {})
    whois_info = crypto_data.get('whois', {})
    geo_info = crypto_data.get('geo', {})
    osint_info = crypto_data.get('osint', {})
    
    def badge(value, expected=None, good='Good', is_tls=False):
        if is_tls:
             if 'Good' in value: return f'<span class="badge" style="background:var(--success); color:white;">{value}</span>'
             else: return f'<span class="badge" style="background:var(--danger); color:white;">{value}</span>'
             
        if isinstance(value, str) and value.lower() in ['missing', 'invalid', 'hidden', 'unknown', 'true', 'false']:
            if value.lower() == 'true' and expected is False:
                return f'<span class="badge" style="background:var(--danger); color:white;">Yes</span>'
            elif value.lower() == 'false' and expected is False:
                return f'<span class="badge" style="background:var(--success); color:white;">No</span>'
            elif value.lower() == 'missing' or (value.lower() == 'true'):
                return f'<span class="badge" style="background:var(--warning); color:white;">{value}</span>'
            return f'<span class="badge badge-secondary" style="background:#e2e8f0; color:#475569;">{value}</span>'
            
        if expected is not None:
            if value == expected:
                return f'<span class="badge" style="background:var(--success); color:white;">{good}</span>'
            else:
                if ssl_info.get('blocked'):
                     return f'<span class="badge" style="background:var(--warning); color:white;">Domain Blocked</span>'
                return f'<span class="badge" style="background:var(--danger); color:white;">High Risk</span>'
                
        return f'<span class="badge" style="background:var(--primary); color:white;">{value}</span>'

    tls_versions_html = ""
    for tls_ver, strength in ssl_info.get("tls_versions", []):
        tls_versions_html += f"<div>{tls_ver}: {badge(strength, is_tls=True)}</div>"
    if not tls_versions_html:
        tls_versions_html = "<div><span class='badge badge-secondary' style='background:#e2e8f0; color:#475569;'>Unknown - Detection failed</span></div>"
        
    ssl_error_html = f" <span style='color:var(--danger); font-size:13px; font-weight:500; margin-left:8px;'>({ssl_info.get('error', 'Validation Failed')})</span>" if not ssl_info.get('valid') and ssl_info.get('error') else ""

    osint_html = ""
    if osint_info.get('subdomains'):
        osint_html = f"""
            <div class="card">
                <div class="section-title">OSINT & Web Footprint</div>
                <table>
                    <tbody>
                        <tr><td width="30%">Public Subdomains (Top 15 via crt.sh & HackerTarget)</td><td>{'<br>'.join(f"<span>{s}</span>" for s in osint_info['subdomains'])}</td></tr>
                    </tbody>
                </table>
            </div>"""

    return f"""
            <div class="card">
                <div class="section-title">SSL / TLS Configuration</div>
                <table>
                    <tbody>
                        <tr><td width="30%">Valid Certificate</td><td>{badge(ssl_info.get('valid', 'Unknown'), expected=True, good='Yes')}{ssl_error_html}</td></tr>
                        <tr><td>Expired</td><td>{badge(str(ssl_info.get('expired', 'Unknown')), expected=False, good='No')}</td></tr>
                        <tr><td>Self-Signed</td><td>{badge(str(ssl_info.get('self_signed', 'Unknown')), expected=False, good='No')}</td></tr>
                        <tr><td>Wrong Hostname</td><td>{badge(str(ssl_info.get('wrong_hostname', 'Unknown')), expected=False, good='No')}</td></tr>
                        <tr><td>Issuer</td><td><span class="badge badge-secondary" style="background:#e2e8f0; color:#475569;">{ssl_info.get('issuer', 'Unknown')}</span></td></tr>
                        <tr><td>Expiry Date</td><td><span class="badge badge-secondary" style="background:#e2e8f0; color:#475569;">{ssl_info.get('not_after', 'Unknown')}</span></td></tr>
                        <tr><td>Supported TLS Versions</td><td>{tls_versions_html}</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="section-title">Security Headers</div>
                <table>
                    <tbody>
                        <tr><td width="30%">Strict-Transport-Security</td><td>{badge(headers_info.get('Strict-Transport-Security', 'Missing'))}</td></tr>
                        <tr><td>Content-Security-Policy</td><td>{badge(headers_info.get('Content-Security-Policy', 'Missing'))}</td></tr>
                        <tr><td>X-Content-Type-Options</td><td>{badge(headers_info.get('X-Content-Type-Options', 'Missing'))}</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="section-title">Server Banner Information</div>
                <table>
                    <tbody>
                        <tr><td width="30%">Server</td><td><span class="badge" style="background:var(--primary); color:white;">{banner_info.get('Server', 'Hidden')}</span></td></tr>
                        <tr><td>X-Powered-By</td><td><span class="badge" style="background:var(--warning); color:white;">{banner_info.get('X-Powered-By', 'Hidden')}</span></td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="section-title">WHOIS Information</div>
                <table>
                    <tbody>
                        <tr><td width="30%">Registrar</td><td><strong>{whois_info.get('Registrar', 'Unknown')}</strong></td></tr>
                        <tr><td>Creation Date</td><td>{whois_info.get('Creation Date', 'Unknown')}</td></tr>
                        <tr><td>Expiry Date</td><td>{whois_info.get('Expiry Date', 'Unknown')}</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="section-title">IP Geolocation</div>
                <table>
                    <tbody>
                        <tr><td width="30%">IP Address</td><td><strong>{geo_info.get('IP', 'Unknown')}</strong></td></tr>
                        <tr><td>Country</td><td>{geo_info.get('Country', 'Unknown')}</td></tr>
                        <tr><td>Hosting Provider / ISP</td><td>{geo_info.get('Hosting Provider', 'Unknown')}</td></tr>
                    </tbody>
                </table>
            </div>
            {osint_html}
"""

def generate_crypto_html(report_data, target, output_dir=None):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    domain = report_data.get('domain', target)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cryptography Scan Report - {domain}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #2563eb;
                --secondary: #64748b;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --dark: #0f172a;
                --light: #f8fafc;
                --surface: #ffffff;
                --border: #e2e8f0;
            }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; background-color: #f1f5f9; color: #334155; line-height: 1.6; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 40px 0; margin-bottom: -60px; padding-bottom: 80px; }}
            .header-content {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
            .logo h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
            .logo p {{ margin: 5px 0 0; opacity: 0.8; font-size: 14px; }}
            .card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 24px; margin-bottom: 24px; border: 1px solid var(--border); }}
            .section-title {{ font-size: 18px; font-weight: 600; color: var(--dark); margin-top: 0; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid var(--border); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 12px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--secondary); background: #f8fafc; border-bottom: 1px solid var(--border); }}
            td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 14px; vertical-align: top; }}
            tr:last-child td {{ border-bottom: none; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; color: white;}}
            .font-mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }}
            footer {{ text-align: center; padding: 40px; color: var(--secondary); font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <h1>Cryptography Scan Report</h1>
                    <p>Target: {domain}</p>
                </div>
                <div class="scan-meta">
                    <div>{current_datetime}</div>
                </div>
            </div>
        </div>
        <div class="container">
            {get_crypto_html_snippets(report_data)}
            <footer>
                <p>Generated by Zeuz Security Automation Framework &bull; {current_datetime}</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = '.'
    out_path = os.path.join(output_dir, f"crypto_report_{domain.replace('.', '_')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
         f.write(html_template)
    print(f"Enhanced cryptography report saved: {out_path}")
    return out_path


def cryptography_scan_run(url, security_report_dir=None):
    if hasattr(security_report_dir, 'mkdir'):
        security_report_dir.mkdir(parents=True, exist_ok=True)
    elif security_report_dir:
        os.makedirs(security_report_dir, exist_ok=True)
        
    print(f"Running Cryptography scan for {url}...")
    
def get_cryptography_data(url):
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.split(':')[0]
    
    report_data = {
        "domain": domain,
        "url": url,
        "ssl": {"valid": False, "expired": False, "self_signed": False, "wrong_hostname": False, "tls_versions": []},
        "headers": {},
        "banner": {},
        "whois": {},
        "geo": {}
    }
    # 1. SSL Certificate Info
    print(f"[{domain}] Fetching SSL/TLS Certificate information...", flush=True)
    try:
        context = ssl.create_default_context()
        try:
             with socket.create_connection((domain, 443), timeout=2) as sock:
                 with context.wrap_socket(sock, server_hostname=domain) as ssock:
                     cert = ssock.getpeercert()
                     report_data['ssl']['expired'] = ssl.cert_time_to_seconds(cert['notAfter']) < time.time()
                     
                     issuer = dict(x[0] for x in cert.get('issuer', []))
                     subject = dict(x[0] for x in cert.get('subject', []))
                     report_data['ssl']['self_signed'] = issuer == subject
                     
                     report_data['ssl']['valid'] = True
                     report_data['ssl']['not_after'] = cert['notAfter']
                     report_data['ssl']['issuer'] = issuer.get('organizationName', issuer.get('commonName', 'Unknown'))
                     
                     # Check TLS Version while socket is open
                     ver = ssock.version()
                     if ver:
                         strength = 'Good' if ver in ['TLSv1.2', 'TLSv1.3'] else 'Weak'
                         report_data['ssl']['tls_versions'] = [(ver, strength)]
                         
        except ssl.CertificateError as e:
            report_data['ssl']['wrong_hostname'] = True
            report_data['ssl']['valid'] = False
            report_data['ssl']['error'] = str(e)
            
            # Reconnect without verification to get cert info anyway
            ctx_no_verify = ssl._create_unverified_context()
            with socket.create_connection((domain, 443), timeout=2) as sock:
                 with ctx_no_verify.wrap_socket(sock, server_hostname=domain) as ssock:
                     cert = ssock.getpeercert()
                     if cert:
                         report_data['ssl']['expired'] = ssl.cert_time_to_seconds(cert['notAfter']) < time.time()
                         issuer = dict(x[0] for x in cert.get('issuer', []))
                         report_data['ssl']['not_after'] = cert['notAfter']
                         report_data['ssl']['issuer'] = issuer.get('organizationName', issuer.get('commonName', 'Unknown'))
                     ver = ssock.version()
                     if ver:
                         strength = 'Good' if ver in ['TLSv1.2', 'TLSv1.3'] else 'Weak'
                         report_data['ssl']['tls_versions'] = [(ver, strength)]
    except Exception as e:
        report_data['ssl']['valid'] = 'Error'
        report_data['ssl']['error'] = str(e)
        if '[Errno 54]' in str(e) or 'timed out' in str(e).lower() or 'Connection refused' in str(e):
            report_data['ssl']['blocked'] = True
            print(f"[{domain}] WARNING: Access Blocked/Reset by Domain Firewall/WAF.", flush=True)

    # 2. HTTP Headers & Server Banner
    print(f"[{domain}] Fetching HTTP Security Headers...", flush=True)
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, context=ctx, timeout=2) as resp:
            headers = resp.headers
    except urllib.error.HTTPError as e:
        headers = e.headers
    except Exception as e:
        headers = {}
        report_data['headers']['error'] = str(e)

    if headers:
        report_data['headers'] = {
            "Strict-Transport-Security": headers.get("Strict-Transport-Security", "Missing"),
            "Content-Security-Policy": headers.get("Content-Security-Policy", "Missing"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options", "Missing")
        }
        report_data['banner'] = {
            "Server": headers.get("Server", "Hidden"),
            "X-Powered-By": headers.get("X-Powered-By", headers.get("X-Powered-By-Plesk", "Hidden"))
        }

    # 3. IP Geolocation ONLY
    print(f"[{domain}] Fetching IP Geolocation...", flush=True)
    try:
        ip = socket.gethostbyname(domain)
        geo_req = urllib.request.Request(f"http://ip-api.com/json/{ip}")
        with urllib.request.urlopen(geo_req, timeout=2) as geo_resp:
            geo_data = json.loads(geo_resp.read().decode())
            report_data['geo'] = {
                "IP": ip,
                "Country": geo_data.get("country", "Unknown"),
                "Hosting Provider": geo_data.get("isp", geo_data.get("org", "Unknown"))
            }
    except Exception as e:
        report_data['geo'] = {"IP": socket.gethostbyname(domain) if 'domain' in locals() else 'Unknown'}

    return report_data


def cryptography_scan_run(url, security_report_dir=None):
    if hasattr(security_report_dir, 'mkdir'):
        security_report_dir.mkdir(parents=True, exist_ok=True)
    elif security_report_dir:
        os.makedirs(security_report_dir, exist_ok=True)
        
    print(f"Running Cryptography scan for {url}...")
    
    report_data = get_cryptography_data(url)
    domain = report_data.get("domain", url)

    html_result = generate_crypto_html(report_data, domain, security_report_dir)
    print("Cryptography scan complete!")
    return {
        "report_data": report_data,
        "html": html_result
    }