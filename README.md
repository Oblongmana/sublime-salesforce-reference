# Sublime Salesforce Reference

A plugin for Sublime Text that gives you quick access to Salesforce Documentation from Sublime Text.

## Installation

1. **Recommended:** Download [Package Control](http://wbond.net/sublime_packages/package_control) and install using the *Package Control: Install Package* command (search for *Salesforce Reference*)
2. **Not recommended:** Simply download this repo and save it to a *SublimeSalesforceReference* directory inside your Sublime Packages/ directory. You will not receive automatic updates as you would following option 1

## Usage 

SublimeSalesforceReference adds multiple new commands to your palette:
  - `Salesforce Reference - Apex`
  - `Salesforce Reference - Visualforce`
  - `Salesforce Reference - Service Console`
  - `Salesforce Reference - All Documentation Types` 

Simply select one of these command, and the plugin will retrieve an index of reference pages from Salesforce and show them to you in a quick panel. Search for what you're after, press enter, and the documentation page will open in your web browser!

Each of the commands is reasonably self-explanatory - the `Salesforce Reference - Apex` command shows the a list of Apex documentation pages, and so on; while the `Salesforce Reference - All Documentation Types` shows in a single list the documentation for all doc types this plugin supports.

![](http://jameshill.io/images/doc/sublime-salesforce-reference/usage.png)

By default, when Sublime Text starts up, the plugin will make a callout to cache the Salesforce Reference Index for the `Apex` and `Visualforce` documentation, so that when you run a `Salesforce Reference` command, the list of reference pages will open instantly. You can disable the cache-on-load behaviour (see the Settings section for how to do so), in which case the cache will be filled the first time you run the command. You can also specify which types of documentation should be cached (for example, by default the `Service Console` documentation is not cached on load - but you can make it so!)

## Settings

To edit your settings, go to Preferences > Package Settings > Salesforce Reference > Settings - User

``` javascript
{
    /*  refreshCacheOnLoad:
    *
    *  Setting this to false means the plugin will need to do a callout
    *      to retrieve the Salesforce Reference Index from Salesforce
    *     when the *Salesforce Reference* command is first run.
    *
    *      When set to true (RECOMMENDED, and the default setting), the
    *      plugin will cache the Reference Index when Sublime Text starts
    *      or the plugin is reloaded
    */
    "refreshCacheOnLoad": true,
    
    /**
     *  docTypes:
     *
     *  Each docType has one option:
     *   - refreshCacheOnLoad:
     *       if the top-level refreshCacheOnLoad setting is true, and this
     *       docType's refreshCacheOnLoad setting is true - this documentation
     *       type will be cache when sublime starts up. Otherwise, this
     *       documentation type will only be retrieved and cached when it's
     *       corresponding command is run
     *   - excludeFromAllDocumentationCommand:
     *       if this is set to true, the command "Salesforce Reference - All
     *       Documentation Types" will not include this documentation type.
     *       If set to false for a documentation type, uou'll only be able to
     *       view that documentation type with from the command specific to it,
     *       it won't be included in the command "Salesforce Reference - All
     *       Documentation Types"
     *
     *  Note to developers: the keys in `docTypes` should be an exact lowercase
     *   match of one of the keys in salesforce_reference.retrieve.DocTypeEnum
     */
    "docTypes": {
      "apex": {
        "refreshCacheOnLoad": true,
        "excludeFromAllDocumentationCommand": false
      },
      "visualforce": {
        "refreshCacheOnLoad": true,
        "excludeFromAllDocumentationCommand": false
      },
      "serviceconsole": {
        "refreshCacheOnLoad": false,
        "excludeFromAllDocumentationCommand": false
      }
    }
}
```

## Key bindings

Available commands for key bindings are:

 - `salesforce_reference_apex`
 - `salesforce_reference_visualforce`
 - `salesforce_reference_service_console`
 - `salesforce_reference_all_documentation_types`

To set a key binding to one of these, go to `Preferences > Key Bindings - User`
and insert something like this (for example):
``` javascript
{
    //Example key binding
    "keys": ["alt+s"],
    "command": "salesforce_reference_all_documentation_types"
}
```

## Contributing, Bugs, Suggestions, Questions

If you have any suggestions or bugs to report, please open an issue and I'll take a look ASAP. If you have any questions or would like to contribute in any way, you can also get in touch with me by tweeting [@Oblongmana](http://twitter.com/oblongmana), or go ahead and fork the repo and submit a pull request.

Please note that we will roughly be following semver + git-flow for 2.0.0 onwards. The short version of that is - new branches should be made off the `develop` branch like so:
 - `fix/describe-your-fix` for bug fixes
 - `feature/describe-your-feature` for new features
 - `chore/describe-your-chore` for new things like minor documentation updates
Once complete, merge any remote changes to the `develop` branch into your local branch, and submit a pull request against the `develop` branch

When we're ready for a release, a release candidate will be branched off `develop` into `release-X.Y.Z` (`X.Y.Z` being the version number). This branch will be open to fixes only, no new features. Other maintenance things like release note changes, doc tweaks, will be accepted only if relevant to the release. Once complete, the release branch will be merged into master, tagged, and shipped.

If you don't follow those instructions precisely, it's probably no big deal, we'll try to make it work, but it may take longer or be more of a challenge.

### Adding new documentation sources

If there's a documentation source you want to add, please open an issue for discussion on why it should be included. Note that no documentation sources have been deliberately excluded yet - time to implement is the primary constraint!

Alternatively, if you want to have a go at adding it yourself, `salesforce_reference/retrieve.py` contains the necessary framework for doing so:
 - Create a new `DocRetrievalStrategy`, and add this to the `DocTypeEnum`, including modifying the `DocTypeEnum.get_all()` and `DocTypeEnum.get_by_name()` methods appropriately
 - Add settings for this to `SublimeSalesforceReference.sublime-settings`, under `docTypes`. Make sure the key you add to this is identical to the key you added in `DocTypeEnum`, but in lowercase
 - Add a new command in `SalesforceReference.py`, and create the command palette entry for it in `Default.sublime-commands`

## License

### Sublime Salesforce Reference
Copyright (c) 2014-2015 James Hill <me@jameshill.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


### ThreadProgress.py
ThreadProgress.py is licensed under the MIT license, and SalesforceReference.py's RetrieveIndexThread method derives in part from code under the same license

Copyright (c) 2011-2013 Will Bond <will@wbond.net>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Credits

All Salesforce Documentation is © Copyright 2000–2015 salesforce.com, inc.

Thanks to [Marco Zeuli](https://github.com/maaaaarco) for his contributions to making extra types of documentation available in the plugin

Credit to [Luke McFarlane](https://github.com/lukemcfarlane) for the inspiration!
