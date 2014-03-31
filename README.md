# Sublime Salesforce Reference

A plugin for Sublime Text that gives you quick access to Salesforce Documentation from Sublime Text.

## Installation

1. **Recommended:** Download [Package Control](http://wbond.net/sublime_packages/package_control) and install using the *Package Control: Install Package* command (search for *Salesforce Reference*)
2. **Not recommended:** Simply download this repo and save it to a *SublimeSalesforceReference* directory inside your Sublime Packages/ directory. You will not receive automatic updates as you would following option 1

## Usage 

SublimeSalesforceReference adds a new command to your palette: *'Salesforce Reference'*. Simply select this command, and the plugin will retrieve an index of reference pages from Salesforce and show them to you in a quick panel. Search for what you're after, press enter, and the documentation page will open in your web browser!

![](http://oblongmana.com/images/doc/sublime-salesforce-reference/usage.png)

By default, the plugin will make a callout to cache the Salesforce Reference Index when Sublime Text opens, so that when you run the *Salesforce Reference* command, the list of reference pages will open instantly. You can disable the cache-on-load behaviour (see the Settings section for how to do so), in which case the cache will be filled the first time you run the command.

## Settings

To edit your settings, go to Preferences > Package Settings > Salesforce Reference > Settings - User

``` json
{
    //  refreshCacheOnLoad:
    //
    //  Setting this to false means the plugin will need to do a callout
    //      to retrieve the Salesforce Reference Index from Salesforce
    //      when the *Salesforce Reference* command is first run.
    //
    //      When set to true (RECOMMENDED, and the default setting), the
    //      plugin will cache the Reference Index when Sublime Text starts
    //      or the plugin is reloaded
    "refreshCacheOnLoad": true 
}
```

## Contributing, Bugs, Suggestions, Questions

If you have any suggestions or bugs to report, please open an issue and I'll take a look ASAP. If you have any questions or would like to contribute in any way, you can also get in touch with me by tweeting [@Oblongmana](http://twitter.com/oblongmana), or go ahead and fork the repo and submit a pull request.

## License

Copyright (c) 2014 James Hill <oblongmana@gmail.com>

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


ThreadProgress.py is licensed under the MIT license, and SalesforceReference.py's RetrieveIndexThread method is a derives in part from code under the same license

Copyright (c) 2011-2013 Will Bond <will@wbond.net>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Credits

All Salesforce Documentation is © Copyright 2000–2014 salesforce.com, inc.

Credit to [Luke McFarlane](https://github.com/lukemcfarlane) for the inspiration!
