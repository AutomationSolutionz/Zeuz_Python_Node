# Zeuz Node

## Download

[Releases](https://github.com/AutomationSolutionz/Zeuz_Python_Node/releases) -
From the latest relase, expand the *Assets* section and click on **Source code
(zip)** to download.

## Description

Client side application for running automated tests.

For help and available flags, run: `python node_cli.py --help`

To run Zeuz Node in daemon mode (as a background process), execute the
`daemon.sh` script.

## FAQ

**Q.** I have Python 3.9+ installed. Can I use ZeuZ Node with it?
> Our recommended Python version at the moment is Python 3.8. We have tested all
> the internal modules with this version. However, if you are not doing
> **Windows** automation, it should be fine to run any newer versions of Python.

**Q.** How do I logout?
> Run `python node_cli.py --logout`

**Q.** My webdrivers are not downloading because of SSL certificate verification
   issues.
> Set the `WDM_SSL_VERIFY=0` environment variable, relaunch your terminal and
> run node_cli.py again.

## State diagram

```mermaid
stateDiagram-v2
    direction TB
    state Node {
        direction TB
        dh : deploy_handler
        save_json : Save json to file
        run_tc: Run test case
        run_id_complete: RunID Complete
        deploy_svc_connect: Connect to deploy service

        [*] --> node_cli
        node_cli --> login
        login --> deploy_svc_connect

        deploy_svc_connect --> dh : /zsvc/deploy/v1/connect
        dh --> response_callback : server sends Test Case data
        dh --> done_callback : server sends DONE
        dh --> cancel_callback : server sends CANCEL

        done_callback --> deploy_svc_connect : Start new session
        cancel_callback --> deploy_svc_connect : Stop running and start new session

        response_callback --> proto_adapter
        adapter --> save_json : converts the test case data into node's expected json format
        save_json --> MainDriver : reads the json content

        MainDriver --> run_tc
        run_tc --> report_uploader : Upload test case result
        run_tc --> artifacts_uploader : Upload logs, screenshots, etc

        report_uploader --> run_id_complete
        artifacts_uploader --> run_id_complete
    }
```
