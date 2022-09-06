# Gaarf Cloud Workflow generator

An interactive generator for [Gaarf Workflow](https://github.com/google/ads-api-report-fetcher/tree/main/gcp) - Google Cloud components for running Gaarf (Google Ads API Report Fetcher).

It can be called via `npm init`:

```
npm init gaarf-wf
```

Several additional options are supported:
* debug - more detailed output, create a log file `.create-gaarf-wf-out.log` with std output (stdout/stderr)
* diag - even more details output, forces streaming from all executing commands to console

To pass the options use `--` before them while calling via npm init:
```
npm init gaarf-wf -- --debug
```

## Disclaimer
This is not an officially supported Google product.

Copyright 2022 Google LLC. This solution, including any related sample code or data, is made available on an “as is,” “as available,” and “with all faults” basis, solely for illustrative purposes, and without warranty or representation of any kind. This solution is experimental, unsupported and provided solely for your convenience. Your use of it is subject to your agreements with Google, as applicable, and may constitute a beta feature as defined under those agreements. To the extent that you make any data available to Google in connection with your use of the solution, you represent and warrant that you have all necessary and appropriate rights, consents and permissions to permit Google to use and process that data. By using any portion of this solution, you acknowledge, assume and accept all risks, known and unknown, associated with its usage, including with respect to your deployment of any portion of this solution in your systems, or usage in connection with your business, if at all.
