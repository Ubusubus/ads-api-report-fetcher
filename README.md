Google Ads API Report Fetcher (gaarf)

[![npm](https://img.shields.io/npm/v/google-ads-api-report-fetcher)](https://www.npmjs.com/package/google-ads-api-report-fetcher)
[![Downloads npm](https://img.shields.io/npm/dw/google-ads-api-report-fetcher?logo=npm)](https://www.npmjs.com/package/google-ads-api-report-fetcher)
[![PyPI](https://img.shields.io/pypi/v/google-ads-api-report-fetcher?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/google-ads-api-report-fetcher/)
[![Downloads PyPI](https://img.shields.io/pypi/dw/google-ads-api-report-fetcher?logo=pypi)](https://pypi.org/project/google-ads-api-report-fetcher/)


## Table of content

 - [Overview](#overview)
 - [Getting started](#getting-started)
 - [Writing Queries](#writing-queries)
 - [Running gaarf](#running-gaarf)
     - [Options](#options)
     - [Postprocessing](#postprocessing)
 - [Expressions and Macros](#expressions-and-macros)
     - [Dynamic dates](#dynamic-dates)
 - [Docker](#docker)
 - [Gaarf Cloud Workflow](#gaarf-cloud-workflow)
 - [Differencies in Python and NodeJS versions](#differencies-in-python-and-nodejs-versions)


## Overview

Google Ads API Report Fetcher (`gaarf`) simplifies running [Google Ads API Reports](https://developers.google.com/google-ads/api/fields/v9/overview)
by separating logic of writing [GAQL](https://developers.google.com/google-ads/api/docs/query/overview)-like query from executing it and saving results.\
The library allows you to define GAQL queries alongside aliases and custom extractors and specify where the results of such query should be stored.
You can find example queries in [examples](examples) folder.
Based on such a query the library fill extract the correct GAQL query, automatically extract all necessary fields from schema
and transform them into a structure suitable for writing data.

Currently the tool supports two types of output: CSV files and BigQuery tables.


## Getting started

Google Ads API Report Fetcher has two versions - Python and Node.js.
Please explore the relevant section to install and run the tool:

* [Getting started with gaarf in Python](py/README.md)
* [Getting started with gaarf in Node.js](js/README.md)

Both versions have similar command line arguments and query syntax.


## Writing Queries

Google Ads API Report Fetcher provides an extended syntax on writing GAQL queries.\
Please refer to [How to write queries](docs/how-to-write-queries.md) section to learn the query syntax.


## Running gaarf

If `gaarf` is installed globally you can run it with the following command.

```shell
gaarf <queries> [options]
```

### Options
The required positional arguments are a list of files or a text that contain Ads queries (GAQL).
On *nix OSes you can use a glob pattern, e.g. `./ads-queries/**/*.sql`.
A file path can be not only a local path but also a GCS file.

> If you run the tool on a *nix OS then your shell (like zsh/bash) probably
> supports file names expansion (see [bash](https://www.gnu.org/software/bash/manual/html_node/Filename-Expansion.html),
> [zsh](https://zsh.sourceforge.io/Doc/Release/Expansion.html), 14.8 Filename Generation).
> And so it does expansion of glob pattern (file mask) into a list of files.
> Currently the tool doesn't support wildcards for file names (doesn't do expansion) - it's important to understand if you run it in an environment that doesn't support expansion.

Options:
* `ads-config` - a path to yaml file with config for Google Ads,
               by default assuming 'google-ads.yaml' in the current folder
* `account` - Ads account id, aka customer id, it can contain multiple ids separated with comma, also can be specified in google-ads.yaml as 'customer-id' (as string or list)
* `input` - input type - where queries are coming from (Python only). Supports the following values:
  * `file` - (default) local or remote (GCS, S3, Azure, etc.) files
  * `console` - data are read from standard output
* `output` - output type, Supports the following values:
  * `csv` - write data to CSV files
  * `bq` or `bigquery` - write data to BigQuery
  * `console` - write data to standard output
  * `sqldb` - writes data to a database supported by SQL Alchemy (Python only).
* `loglevel` - logging level: 'debug', 'verbose', 'info', 'warn', 'error'
* `skip-constants` - do not execute scripts for constant resources (e.g. language_constant) (*NodeJS version only*)
* `dump-query` - outputs query text to console after resolving all macros and expressions (*NodeJS version only*), loglevel should be not less than 'verbose'
* `customer-ids-query` - GAQL query that specifies for which accounts you need to run `gaarf`. Must contains **customer.id** as the first column in SELECT statement with all the filtering logic going to WHERE statement.
  `account` argument must be a MCC account id (or accounts) in this case.

  >Example usage: `gaarf <queries> --account=123456 --customer-ids-query='SELECT customer.id FROM campaign WHERE campaign.advertising_channel_type="SEARCH"'`

* `customer-ids-query-file` - the same as `customer-ids-query` but the query is coming from a file (can be a GCS path).

  >Example usage: `gaarf <queries> --account=123456 --customer-ids-query-file=/path/to/query.sql

* `disable-account-expansion` - disable MCC account expansion into child accounts (useful when you need to execute a query at MCC level or for speeding up if you provided leaf accounts).
  By default Gaarf does account expansion (even with `customer-ids-query`).

* `parallel-account` - how one query is being processed for multiple accounts: in parallel (true) or sequentially (false). By default - in parallel (*NodeJS version only*, for Python - always sequentially)
* `parallel-queries` - how to process queries file: all in parallel (true) or sequentially (false). By default - in parallel (*Python version only*, for NodeJS - always sequentially)
* `parallel-threshold` - a number, maximum number of parallel queries (*NodeJS version only*)


Options specific for CSV writer:
* `csv.destination-folder` - output folder where csv files will be created
* `csv.array-separator` - a separator symbol for joining arrays as strings, by default '|' (*NodeJS version only*)
* `csv.file-per-customer` - create a CSV file per customer (default: false) (*NodeJS version only*)

Options specific for BigQuery writer:
* `bq.project` - GCP project id
* `bq.dataset` - BigQuery dataset id where tables with output data will be created
* `bq.location` - BigQuery [locations](https://cloud.google.com/bigquery/docs/locations)
* `bq.table-template`  - template for tables names, `{script}` references script base name, plus you can use [expressions](#expressions-and-macros) (*NodeJS version only*)
* `bq.dump-schema` - flag that enable dumping json files with schemas for tables (*NodeJS version only*)
* `bq.no-union-view` - flag that disables creation of "union" view that combines all customer tables (*NodeJS version only*)
* `bq.array-handling` - arrays handling method: "arrays" (default) - store arrays as arrays (repeated fields), "strings" - store arrays as strings (items combined via a separator, e.g. "item1|item2") (*NodeJS version only*)
* `bq.array-separator` - a separator symbol for joining arrays as strings, by default '|' (*NodeJS version only*)

Options specific for Console writer (*NodeJS version only*):
* `console.transpose` - whenever and how to transpose (switch rows and columns) result tables in output:
`auto` (default) - transpose only if table does not fit into terminal window, `always` - transpose all the time, `never` - never transpose

Options specific for SqlAlchemy writer (*Python version only*):
* `sqldb.connection-string` to specify where to write the data (see [more](https://docs.sqlalchemy.org/en/14/core/engines.html))
* `sqldb.if-exists` - specify how to behave if the table already exists (see [more](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html))


All parameters whose names start with the `macro.` prefix are passed to queries as params object.
For example if we pass parameters: `--macro.start_date=2021-12-01 --macro.end_date=2022-02-28`
then inside sql we can use `start_date` and `end_date` parameters in curly brackets:
```sql
    AND segments.date >= "{start_date}"
    AND segments.date <= "{end_date}"
```

Full example:
```
gaarf google_ads_queries/*.sql --ads-config=google-ads.yaml \
  --account=1234567890 --output=bq \
  --macro.start_date=2021-12-01 \
  --macro.end_date=2022-02-28 \
  --bq.project=my_project \
  --bq.dataset=my_dataset
```

If you run Python version of `gaarf` you can provide query directly from console:

```
gaarf 'SELECT campaign.id FROM campaign WHERE campaign.advertising_channel_type="SEARCH"' \
  --account=1234567890 --input=console --output=console
```
`gaarf` will read text from console and returns results back to console.


For NodeJS version any of arguments can be specified via environment variable which name starts with "GAARF_" (e.g. GAARF_ACCOUNT).


### Postprocessing

Once reports have been fetched you might use `gaarf-bq` or `gaarf-sql` (utilities that installed alongside with `gaarf`) to run queries in BigQuery or any other DB supposed by SqlAlchemy based on collected data in there.
Essentially it's a simple tool for executing queries from files, optionally creating tables for query results.


```shell
gaarf-bq <files> [options]
gaarf-sql <files> [options]
```

Options:
* `sql.*` - named SQL parameters to be used in queries as `@param`. E.g. a parameter 'date' supplied via cli as `--sql.date=2022-06-01` can be used in query as `@date` in query.
* `macro.*` - macro parameters to substitute into queries as `{param}`. E.g. a parameter 'dataset' supplied via cli as `--macro.dataset=myds` can be used as `{dataset}` in query's text.
* `template.*` -  parameters for templates, strings with "," will be converted to lists/arrays

 
The tool assumes that scripts you provide are DDL, i.e. contains statements like create table or create view.

In general it's recommended to separate tables with data from Ads API and final tables/views created by your post-processing queries.

**BigQuery specific options:**

* `project` - GCP project id
* `dataset-location` - BigQuery [locations](https://cloud.google.com/bigquery/docs/locations) for newly created dataset(s)

So it's likely that your final tables will be in a separate dataset (or datasets). To allow the tool to create those datasets for you, make sure that macro for your datasets contains the word "dataset".
In that case gaarf-bq will check that a dataset exists and create it if not.


For example:
```
CREATE OR REPLACE TABLE `{dst_dataset}.my_dashboard_table` AS
SELECT * FROM {ads_ds}.{campaign}
```
In this case gaarf-bq will check for existance of a dataset specified as 'dst_dataset' macro.

**SqlAlchemy specific options [Python only]:**
* `connection-string` - specific connection to the selected DB (see [more](https://docs.sqlalchemy.org/en/14/core/engines.html))

Connection string can be:
* raw text (i.e. `sqlite:///gaarf.db`)
* parameterized string relying on environmental variables
(i.e. `postgresql+psycopg2://{GAARF_USER}:{GAARF_PASSWORD}@{GAARF_DB_HOST}:{GAARF_DB_PORT}/{GAARF_DB_NAME}`).

If the connection string relies on parameters, please export them:

```
export GAARF_USER=test
export GAARF_PASSWORD=test
export GAARF_DB_HOST=test
export GAARF_DB_PORT=12345
export GAARF_DB_NAME=test
```

**Common options**

There are three type of parameters that you can pass to a script: `macro`, `sql`, and `template`.

*Macro*

Macro is just a substitution in script text.
For example:
```
SELECT *
FROM {dst_dataset}.{table-src}
```
Here `dst_dataset` and `table-src` are macros that can be supplied as:
```
gaarf-bq --macro.table-src=table1 --macro.dst_dataset=dataset1
```

*SQL*

You can also use normal sql type parameters with `sql` argument:
```
SELECT *
FROM {dst_dataset}.{table-src}
WHERE name LIKE @name
```
and to execute:
`gaarf-bq --macro.table-src=table1 --macro.dst_dataset=dataset1 --sql.name='myname%'`

it will create a parameterized query to run in BQ:
```
SELECT *
FROM dataset1.table1
WHERE name LIKE @name
```

*Template*

Your SQL scripts can be templates using a template engine: [Jinja](https://jinja.palletsprojects.com) for Python and [Nunjucks](https://mozilla.github.io/nunjucks/) for NodeJS.
A script will be processed as a template if and only if you supplied `template` argument.

Inside templates you can use appropriate syntax and control structues of a template engine (Jinja/Nunjucks).
They are mostly compatible but please consult the documentations if you migrate between platforms (Python <-> NodeJS).

Usually inside template blocks you use some variable (in if-else/for-loop). To pass their values you use `--template` arguments.

Example:
```
SELECT
  customer_id AS
  {% if level == "0"  %}
  root_account_id
  {% else %}
  leaf_account_id
  {% endif %}
FROM dataset1.table1
WHERE name LIKE @name
```
and to execute:

`gaarf-bq path/to/query.sql --template.level=0`

This will create a column named either `root_account_id` since the specified level is 0.

Please note that all values passed through CLI arguments are strings. But there's a special case - a value containing ","
then it's treated as an array - see the following example.

Template are great when you need to create multiple column based on condition:

```
SELECT
    {% for day in cohort_days %}
        SUM(GetCohort(lag_data.installs, {{day}})) AS installs_{{day}}_day,
    {% endfor %}
FROM asset_performance
```
and to execute:

`gaarf-bq path/to/query.sql --template.cohort_days=0,1,3,4,5,10,30`

It will create 7 columns (named `installs_0_day`, `installs_1_day`, etc) because the cohort_days argument was processed as a list.

ATTENTION: passing macros into sql queries is vulnerable to sql-injection so be very careful where you're taking values from.


## Expressions and Macros
> *Note*: currently expressions are supported only in NodeJS version.

As noted earlier both Ads queries and BigQuery queries support macros. They are named values than can be passed alongside
parameters (e.g. command line, config files) and substituted into queries. Their syntax is `{name}`.
On top of this queries can contain expressions. The syntax for expressions is `${expression}`.
They will be executed right after macros substitution. So macros can contain expressions inside.
Both expressions and macros deal with query text before submitting it for execution.
Inside expression block we can do anything that the MathJS library supports - see https://mathjs.org/docs/index.html,
plus work with date and time. It's all sort of arithmetic operations, strings and dates manipulations.

One typical use-case - evaluate date/time expressions to get dynamic date conditions in queries. These are when you don't provide
a specific date but evaluate it right in the query. For example, applying a condition for date range for last month,
which can be expressed as a range from today minus 1 month to today (or yesterday):
```
WHERE start_date >= '${today()-period('P1M')}' AND end_date <= '${today()}'
```
will be evaluated to:
`WHERE start_date >= '2022-06-20 AND end_date <= '2022-07-20'`
if today is 2022 July 20th.

Also you can use expressions for making table names dynamic (in BQ scripts), e.g.
```
CREATE OR REPLACE TABLE `{bq_dataset}_bq.assetssnapshots_${format(yesterday(),'yyyyMMdd')}` AS
```

Supported functions:
* `datetime` - factory function to create a DateTime object, by default in ISO format (`datetime('2022-12-31T23:59:59')`) or in a specified format in the second argument (`datetime('12/31/2022 23:59','M/d/yyyy hh:mm')`)
* `date` - factory function to create a Date object, supported formats: `date(2022,12,31)`, `date('2022-12-31')`, `date('12/31/2022','M/d/yyyy')`
* `duration` - returns a Duration object for a string in [ISO_8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) format (PnYnMnDTnHnMnS)
* `period` - returns a Period object for a string in [ISO_8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) format (PnYnMnD)
* `today` - returns a Date object for today date
* `yesterday` - returns a Date object for yesterday date
* `tomorrow` - returns a Date object for tomorrow date
* `now` - returns a DateTime object for current timestamp (date and time)
* `format` - formats Date or DateTime using a provided format, e.g. `${format(date('2022-07-01'), 'yyyyMMdd')}` returns '20220701'

Please note functions without arguments still should called with brackets (e.g. `today()`)

For dates and datetimes the following operations are supported:
* add or subtract Date and Period, e.g. `today()-period('P1D')` - subtract 1 day from today (i.e. yesterday)
* add or subtract DateTime and Duration, e.g. `now()-duration('PT12H')` - subtract 12 hours from the current datetime
* for both Date and DateTime add or subtract a number meaning it's a number of days, e.g. `today()-1`
* subtract two Dates to get a Period, e.g. `tomorrow()-today()` - subtract today from tomorrow and get 1 day, i.e. 'P1D'
* subtract two DateTimes to get a Duration - similar to subtracting dates but get a duration, i.e. a period with time (e.g. PT10H for 10 hours)

By default all dates will be parsed and converted from/to strings in [ISO format]((https://en.wikipedia.org/wiki/ISO_8601)
(yyyy-mm-dd for dates and yyyy-mm-ddThh:mm:ss.SSS for datetimes).
But additionally you can specify a format explicitly (for parsing with `datetime` and `date` function and formatting with `format` function)
using standard [Java Date and Time Patterns](https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html):

* G   Era designator
* y   Year
* Y   Week year
* M   Month in year (1-based)
* w   Week in year
* W   Week in month
* D   Day in year
* d   Day in month
* F   Day of week in month
* E   Day name in week (e.g. Tuesday)
* u   Day number of week (1 = Monday, ..., 7 = Sunday)
* a   Am/pm marker
* H   Hour in day (0-23)
* k   Hour in day (1-24)
* K   Hour in am/pm (0-11)
* h   Hour in am/pm (1-12)
* m   Minute in hour
* s   Second in minute
* S   Millisecond
* z   Time zone - General time zone (e.g. Pacific Standard Time; PST; GMT-08:00)
* Z   Time zone - RFC 822 time zone (e.g. -0800)
* X   Time zone - ISO 8601 time zone (e.g. -08; -0800; -08:00)

Examples:
```
${today() - period('P2D')}
```
output: today minus 2 days, e.g. '2022-07-19' if today is 2022-07-21

```
${today()+1}
```
output: today plus 1 days, e.g. '2022-07-22' if today is 2022-07-21

```
${date(2022,7,20).plusMonths(1)}
```
output: "2022-08-20"


### Dynamic dates
Macro values can contain a special syntax for dynamic dates. If a macro value starts with *:YYYY* it will be processed
as a dynamic expression to calculate a date based on the current date.
The syntax is: `:PATTERN-N`,
where N is a number of days/months/years and PATTERN is one of the following:
* *:YYYY* - current year, `:YYYY-1` - one year ago
* *:YYYYMM* - current month, `:YYYYMM-2` - two months ago
* *:YYYYMMDD* - current date, `:YYYYMMDD-7` - 7 days ago

Example with providing values for macro start_date and end_date (that can be used in queries as date range) as
a range from 1 month ago to yesterday:
```
gaarf google_ads_queries/*.sql --ads-config=google-ads.yaml \
  --account=1234567890 --output=bq \
  --macro.start_date=:YYYYMM-1 \
  --macro.end_date=:YYYYMMDD-1 \
```
So if today is 2022-07-29 then start_date will be '2022-06-29' (minus one month) and
end_date will be '2022-07-28' (minus one day).


> NOTE: dynamic date macro (:YYYY) can be defined as expressions as well (e.g. `${today()-1}` instead of ':YYYYMMDD-1')
> so they are two alternatives. But with expressions you won't need to provide any arguments.
> With expressions we'll have easier deployment (no arguments needed) but
> with dynamic date macro more flexibility if you need to provide different values (sometimes dynamic, sometimes fixed).


If you need to get the current date value in your query you can use a special macro `date_iso` that both versions support.
In runtime you can assume that its value is always provided with the current date in the YYYYMMDD format.
But you can override it via arguments if needed (e.g. `--macro.date_iso=:YYYYMMDD-1`).


## Docker
You can run Gaarf as a Docker container. At the moment we don't publish container images so you'll need to build it on your own.
The repository contains sample `Dockerfile`'s for both versions ([Node](js/Dockerfile)/[Python](py/Dockerfile))
that you can use to build a Docker image.

### Build a container image
If you cloned the repo then you can just run `docker build` (see below) inside it (in js/py folders) with the local [Dockerfile](js/Dockerfile).
Otherwise you can just download `Dockerfile` into an empty folder:
```
curl -L https://raw.githubusercontent.com/google/ads-api-report-fetcher/main/js/Dockerfile > Dockerfile
```

Sample Dockerfile's don't depend on sources, they install gaarf from registries for each platform (npm and PyPi).
To build an image with name 'gaarf' (the name is up to you but you'll use it to run a container later) run
the following command in a folder with `Dockerfile`:
```
sudo docker build . -t gaarf
```
Now you can run a container from this image.

### Run a container
For running a container you'll need the same parameters as you would provide for running it in command line
(a list of ads scripts and a Ads API config and other parameters) and authentication for Google Cloud if you need to write data to BigQuery.
The latter is achievable via declaring `GOOGLE_APPLICATION_CREDENTIALS` environment variable with a path to a service account key file.

You can either embed all them into the image on build or supply them in runtime when you run a container.

The aforementioned `Dockerfile` assumes the following:
* You will provide a list of ads script files
* Application Default Credentials is set with a service account key file as `/app/service_account.json`

So you can map your local files onto these paths so that Gaarf inside a container will find them.
Or copy them before building, so they will be embedded into the image.

This is an example of running Gaarf (Node version) with mapping local files, assuming you have `.gaarfrc` and `service_account.json` in the current folder:
```
sudo docker run --mount type=bind,source="$(pwd)/.gaarfrc",target=/app/.gaarfrc \
  --mount type=bind,source="$(pwd)/ads-scripts",target=/app/ads-scripts \
  --mount type=bind,source="$(pwd)/service_account.json",target=/app/service_account.json \
  gaarf ./ads-scripts/*.sql
```
Here we mapped local `.gaarfrc` with with all parameters (alternatively you can pass them explicitly in command line),
mapped a local service_account.json file with SA keys for authenticating in BigQuery, mapped a local folder "ads-scripts"
with all Ads scripts that we're passing by wildcard mask (it'll be expanded to a list of files by your shell).


## Gaarf Cloud Workflow
Inside [gcp](gcp) folder you can find code for deploying Gaarf to Google Cloud. There are the following components provided:
* Cloud Function (in [gcp/functions](gcp/functions) folder) - two CFs that you can use for running gaarf with scripts located on GCS
* Cloud Workflow (in [gcp/workflow](gcp/workflow) folder) - a Cloud Workflow that orchestrates enumeration scripts on GCS and calling CFs

Please see the [README](gcp/README.md) there for all information.


## Differences in Python and NodeJS versions

### Query syntax and features
There are differences in which features supported for queries.
Python-only features:
* pre-process query files as Jinja templates

NodeJS-only features:
* expressions (${...})
* functions

### Output BigQuery structure
There are differences in how tools process Ads queries.
Python version sends queries to Ads API and parses the result. From the result it creates a BigQuery schema. That's becasue tables in BQ are created only when a query retuned some data.
NodeJS on the contrary parses queries and initializes BigQuery schema before execution. So that it creates BQ tables regardless of the results.

There are differences in BigQuery table structures as well.
Python version creates one table per script. While NodeJS creates a table per script per customer and then creates a view to combine all customer tables.
For example, you have a query campaign.sql. As a result you'll get a querable source 'campaign' in BigQuery in any way. But for Python version it'll be a table.
For NodeJS it'll be a view like `create view dataset.campaign as select * from campaign_* when _TABLE_PREFIX in (cid1,cid2)`, where cid1, cid2 are customer id you supplied.

From Ads API we can get arrays, structs and arrays of arrays or structs. In Python version all arrays will be degrated to string with "|" separator.
In NodeJS version the result will be a repeated field (array).
If values of an array from Ads API are also arrays or structs, they will be converted to JSON.
Though in NodeJS you can tune how to process arrays. The described behavior is by default. You can change it via `bq.array-handling` argument.

### API support
Python version supports any API version (currently available).
While as NodeJS parses query structure it supports only one particular version (it's printed when you run `gaarf` without arguments).


## Disclaimer
This is not an officially supported Google product.
