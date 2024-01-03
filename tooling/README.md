# Tooling

## `cancel-pipelines.py`

CircleCI has no configurable timeout for Pipelines. Because of the inherent way this
tap works, it **does not** sync _beyond_ any running Pipeline. Use this script to
effectively enforce a timeout for your Pipelines to unblock your tap.

```
EXPORT CIRCLE_TOKEN=<Personal API Token>
python cancel-pipelines.py gh/your-org/your-repo 2022-01-01 2022-12-15
```

### Args

Use `start` and `end` to limit the scope of your cancelling.

| Name         | Type       | Description                                                                                                                                                                        |
| ------------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CIRCLE_TOKEN | `envvar`   | [Personal API Token](https://circleci.com/docs/managing-api-tokens/#creating-a-personal-api-token)                                                                                 |
| project slug | `string`   | https://circleci.com/docs/api/v2/index.html#operation/listPipelinesForProject "Example: gh/CircleCI-Public/api-preview-docs, Project slug in the form vcs-slug/org-name/repo-name" |
| start        | `datetime` | Probably your bookmark value, Example: 2022-08-08T06:50:57.723Z                                                                                                                    |
| end          | `datetime` | Any Pipeline which has been updated after this datetime won't be cancelled. Example: 2022-08-08T06:50:57.723Z                                                                      |

## `plan-usage-parser`

CircleCI offers a downloadable `Usage` report. While all of the data we might ever want lives in their API, it is behind their GraphQL-Unstable API, which, understandably, is somewhat ill-advised to build upon.

To see your `Usage` report, go here: https://app.circleci.com/settings/plan/github/(YOUR ORG HERE)/usage

As a stop gap, we offer up this tool to parse the CSV they generate for `Usage`. As written, the CSV is tough to us for historical time series stores. An example file has been included alongside this `README`: `plan-usage-example.csv`

At its core, the file is broken up as follows:

```csv
Header

Date Headers which define all values in columns below here, month 0, month 1, ...
Summary
...

Description text row

Project based credit usage #, ...
project a, month 0, month 1, ...
project b, month 0, month 1, ...

Resource class based credit usage #, ...
resource a, month 0, month 1, ...
resource b, month 0, month 1, ...

User seat credits usage #,month 0, month 1, ...
User seat spend $, month 0, month 1, ...

Footer
```

Each value in `month 0`/`month 1`, is of the format `NNNN (F.F%)`. ie, a whole number (credits) followed by the percentage of the whole that value is. So, our parser also cleans those up.

### Args

| Name                    | Type   | Description                   |
| ----------------------- | ------ | ----------------------------- |
| (position 0: File Path) | String | Path to the CSV file to parse |

### Output

```s
$ python3 tooling/plan-usage-parser.py tooling/plan-usage-example.csv                                                                   
```

```csv
year_month,detail,usage_type,credits
2023-01-01T00:00:00+00:00,mercury,project,271
2023-02-01T00:00:00+00:00,mercury,project,295
2023-03-01T00:00:00+00:00,mercury,project,290
2023-04-01T00:00:00+00:00,mercury,project,196
2023-05-01T00:00:00+00:00,mercury,project,336
2023-06-01T00:00:00+00:00,mercury,project,359
2023-07-01T00:00:00+00:00,mercury,project,349
2023-08-01T00:00:00+00:00,mercury,project,473
2023-09-01T00:00:00+00:00,mercury,project,463
2023-10-01T00:00:00+00:00,mercury,project,376
2023-11-01T00:00:00+00:00,mercury,project,484
2023-12-01T00:00:00+00:00,mercury,project,818
2023-01-01T00:00:00+00:00,venus,project,241
2023-02-01T00:00:00+00:00,venus,project,161
2023-03-01T00:00:00+00:00,venus,project,302
2023-04-01T00:00:00+00:00,venus,project,196
2023-05-01T00:00:00+00:00,venus,project,501
2023-06-01T00:00:00+00:00,venus,project,407
2023-07-01T00:00:00+00:00,venus,project,582
2023-08-01T00:00:00+00:00,venus,project,388
2023-09-01T00:00:00+00:00,venus,project,361
2023-10-01T00:00:00+00:00,venus,project,296
2023-11-01T00:00:00+00:00,venus,project,263
2023-12-01T00:00:00+00:00,venus,project,914
2023-01-01T00:00:00+00:00,docker-xlarge,resource,331
2023-02-01T00:00:00+00:00,docker-xlarge,resource,242
2023-03-01T00:00:00+00:00,docker-xlarge,resource,416
2023-04-01T00:00:00+00:00,docker-xlarge,resource,268
2023-05-01T00:00:00+00:00,docker-xlarge,resource,255
2023-06-01T00:00:00+00:00,docker-xlarge,resource,207
2023-07-01T00:00:00+00:00,docker-xlarge,resource,162
2023-08-01T00:00:00+00:00,docker-xlarge,resource,185
2023-09-01T00:00:00+00:00,docker-xlarge,resource,178
2023-10-01T00:00:00+00:00,docker-xlarge,resource,161
2023-11-01T00:00:00+00:00,docker-xlarge,resource,179
2023-12-01T00:00:00+00:00,docker-xlarge,resource,456
2023-01-01T00:00:00+00:00,machine-windows.xlarge,resource,136
2023-02-01T00:00:00+00:00,machine-windows.xlarge,resource,146
2023-03-01T00:00:00+00:00,machine-windows.xlarge,resource,219
2023-04-01T00:00:00+00:00,machine-windows.xlarge,resource,148
2023-05-01T00:00:00+00:00,machine-windows.xlarge,resource,225
2023-06-01T00:00:00+00:00,machine-windows.xlarge,resource,266
2023-07-01T00:00:00+00:00,machine-windows.xlarge,resource,221
2023-08-01T00:00:00+00:00,machine-windows.xlarge,resource,294
2023-09-01T00:00:00+00:00,machine-windows.xlarge,resource,244
2023-10-01T00:00:00+00:00,machine-windows.xlarge,resource,199
2023-11-01T00:00:00+00:00,machine-windows.xlarge,resource,253
2023-12-01T00:00:00+00:00,machine-windows.xlarge,resource,495
2023-01-01T00:00:00+00:00,User seat credits usage #,user_seat,5975
2023-02-01T00:00:00+00:00,User seat credits usage #,user_seat,135
2023-03-01T00:00:00+00:00,User seat credits usage #,user_seat,1475
2023-04-01T00:00:00+00:00,User seat credits usage #,user_seat,1475
2023-05-01T00:00:00+00:00,User seat credits usage #,user_seat,1575
2023-06-01T00:00:00+00:00,User seat credits usage #,user_seat,1675
2023-07-01T00:00:00+00:00,User seat credits usage #,user_seat,1500
2023-08-01T00:00:00+00:00,User seat credits usage #,user_seat,1475
2023-09-01T00:00:00+00:00,User seat credits usage #,user_seat,145
2023-10-01T00:00:00+00:00,User seat credits usage #,user_seat,1600
2023-11-01T00:00:00+00:00,User seat credits usage #,user_seat,1425
2023-12-01T00:00:00+00:00,User seat credits usage #,user_seat,120
```
