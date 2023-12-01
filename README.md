# tap-circleci

## Meltano Extractor Setup

```
meltano add extractor --custom tap-circleci
```
In the interactive portion, use these variables
```
name: tap-circleci
pypi: git+https://github.com/JChouCode/tap-circleci.git
executable: tap-circleci
capabilities: discover,catalog,state
config: project_slugs,token:password
```

## Improvements
This fork improves the tap to handle edge cases that cause errors.
- Edge Case: Job is cancelled and build number is not created, causing a 404 error when requesting unknown build number.
- Improved Bookmarking
- Added `tooling/` for various scripts which help wrangle some of the sharp corners of CircleCI

## Sisu Data - About
This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Circle CI](https://circleci.com/)
- Extracts the following resources:
  - [Pipelines](hhttps://circleci.com/docs/api/v2/#operation/listPipelines)
  - [Workflows](https://circleci.com/docs/api/v2/#operation/listWorkflowsByPipelineId)
  - [Jobs](https://circleci.com/docs/api/v2/#operation/listWorkflowJobs)
  - [Steps](https://circleci.com/docs/api/#single-job)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Quick start

1. Install

   ```bash
   git clone git@github.com:apollographql/tap-circleci.git && cd tap-circleci && pip install -e .
   ```

2. Create a Circle CI access token

   Login to your Circle CI account, go to the
   [Personal API Tokens](https://circleci.com/account/api)
   page, and generate a new token. Copy the token and save it somewhere safe.

3. Create the config file (see below)

   Create a JSON file containing the token you just created as well as the project slug to the project you want to extract data from. Retrieve the project slug
   from the url for a workflow - it should be the VCS your project uses (`gh` for Github or `bb` for Bitbucket), followed by the owner or organization, followed by the repository name
   ex. `gh/singer-io/singer-python`. You can enter multiple project slugs separated by spaces to pull data from multiple projects.

   ```json
   {
     "token": "your-access-token",
     "project_slugs": "gh/singer-io/singer-python gh/singer-io/getting-started"
   }
   ```

4. Run the tap in discovery mode to get catalog.json file

   ```bash
   tap-circleci --config config.json --discover > catalog.json
   ```

5. In the catalog.json file, select the streams to sync

   Each stream in the properties.json file has a "metadata" entry. To select a stream to sync, add
   `{"breadcrumb": [], "metadata": {"selected": true}}` to that stream's "metadata" entry.  
   For example, to sync the pipelines stream:

   ```
   ...
       "type": [
         "null",
         "object"
       ],
       "additionalProperties": false
     },
     "stream": "pipelines",
     "metadata": [{"breadcrumb": [], "metadata": {"selected": true}}]
   },
   ...
   ```

   Another way to select a stream to sync is to add `"selected": true` into that stream's schema:

   ```
   ...
   "tap_stream_id": "workflows",
   "key_properties": [],
   "schema": {
     "selected": true,
     "properties": {
       "_pipeline_id": {
         "type": [
           "null",
           "string"
         ]
   ...
   ```

   Either way is acceptable, but the first way is preferred.

6. Run the application (will print records and other messages to the console)

   `tap-circleci` can be run with:

   ```bash
   tap-circleci --config config.json --catalog catalog.json
   ```

   To save output to a file:

   ```bash
   tap-circleci --config config.json --catalog catalog.json > output.txt
   ```

   It is our intention that this singer tap gets used with a singer target, which will load the output into a database.
   More information on singer targets [here](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-a-singer-tap-with-a-singer-target).

7. To rerun using the last output `STATE` record:

   In your output records, you will see something like:

   ```json
   {
     "type": "STATE",
     "value": {
       "bookmarks": {
         "gh/apollographql/tap-circleci": {
           "pipelines": { "since": "2023-11-15T00:00:00.000000Z" }
         }
       }
     }
   }
   ```

   Select the `value` key, store it to a JSON file, and run:

   ```bash
   tap-circleci --config config.json --catalog catalog.json --state state.json
   ```

## Configuration

Detailed configuration information for the `--config` key.

| key             | type     | default | description                                            |
| --------------- | -------- | ------- | ------------------------------------------------------ |
| `token`         | `string` | `N/A`   | [Personal API Token](https://circleci.com/account/api) |
| `project_slugs` | `string` | `N/A`   | Space ` ` delimited string of CCI project slugs        |

---

Copyright &copy; 2020 Sisu Data
