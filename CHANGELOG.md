# Changelog

* 0.1.0: Initial version
* 0.1.1: Fixed DB creation location
* 0.2.0: Enhancements
  * Better Helpdesk Case generation
  * DB Reconfigure API is reworked
  * DB Activate API is enhanced: credentials validation, support for workload update
* 0.2.1: Backend dependencies are bumped
* 0.2.2: Frontend changes
  * Cosmetic changes of layout
  * Component's prefixes now match a scope. 
    * `c-` for Connect SPA directly borrowed ones
    * `ez-` for Connect SPA components replicas
    * `ui-` for ones imported from Connect UI Toolkit
  * Table columns now may be styled directly with a column descriptor `style` property
* 0.2.3: Better handling of DB and Client Server errors
* 0.3.0: Administrative UI
* 0.3.1: Enhancements
  * Helpdesk Cases are automatically resolved in administrative actions
  * Frontend changes:
    * Added server errors handling
    * Added workload description and external link to docs
* 0.3.2: Backend dependencies are bumped
* 0.3.3: Removed limit of returned DB objects in DB List API
* 0.4.0: Enhancements
  * DB Owner is shown in Databases API and Administrative UI
  * Max number of allowed DB per account can now be set via `DB_MAX_ALLOWED_NUMBER_PER_ACCOUNT` env variable 
  * Frontend changes:
    * 400 and 422 server errors are better handled
* 0.4.1: Frontend improvements
  * Disabled editing of Technical Contact by administrator
  * Trim credentials fields on input
  * Fixed vertical scrolling
  * Fixed radio buttons layout for Safari
  * Improved reliability of several UI pieces
* 0.4.2: Backend dependencies are bumped and GitHub UI unit testing is fixed
* 0.4.3: Backend dependencies are bumped
* 0.4.4:
  * Better representation of DB events (created, updated) in UI
  * Dependencies are bumped
* 0.4.5:
  * Simplification and adjustment of UI dialogs: create, update and reconfigure
  * Other minor UI changes
  * Dependencies are bumped
* 0.4.6:
  * Updated frontend dependencies
  * Updated required node version to v20
  * Updated frontend test action node version to v20
  * Updated ui/config.yml's title
