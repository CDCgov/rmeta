/**
 * @version 4.24.12
 * Date: 2024-12-13T00:34:46.002Z
 */
/* CDC COMMON COMPONENT */

// Establish the CDC namespace
// @TODO: move back to const eventually -
//        too many contrib libs try to redefine currently
window.CDC = window.CDC || {};

(function () {
	'use strict';
	/**
	 * Common methods and utilities
	 * @namespace CDC.Common
	 */
	CDC.Common = {};
	CDC.Common.runtime = CDC.Common.runtime || {};

	/**
	 * Sanitize HTML string
	 * from: https://github.com/cure53/DOMPurify/
	 * @name CDC.Common.cleanHTML
	 * @param {string} content HTML string to sanitize
	 * @returns {string} Sanitized HTML
	 */
	CDC.Common.cleanHTML = function (content) {
		// Make certain DOMPurify script is loaded
		if ('function' !== typeof window.DOMPurify) {
			return content;
		}
		//eslint-disable-next-line
		return DOMPurify.sanitize(content);
	};

	/**
	 * Clean a string for use as an attribute
	 * @name CDC.Common.cleanAttr
	 * @param {string} attribute Element attribute value to clean
	 * @returns {string} Cleaned attibute value
	 */
	CDC.Common.cleanAttr = function (attribute) {
		return String(attribute)
			.trim()
			.replace(/&/g, '&amp;') /* This MUST be the 1st replacement. */
			.replace(/'/g, '&apos;') /* The 4 other predefined entities, required. */
			.replace(/"/g, '&quot;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/\r\n/g, '') /* Must be before the next replacement. */
			.replace(/[\r\n]/g, '');
	};

	/**
	 * Sanitize URL - only tests for XSS issues
	 * from: https://github.com/braintree/sanitize-url
	 * @name CDC.Common.cleanURL
	 * @param {string} targetURL URL to sanitize
	 * @param {any} blankValue [optional] Value to return on blank, default 'about:blank'
	 * @returns {string|any} Returns sanitized URL, or if unsafe, 'about:blank' or blankValue param
	 */
	CDC.Common.cleanUrl = function (targetURL, blankValue) {
		blankValue = undefined === blankValue ? 'about:blank' : blankValue;
		var urlScheme, urlSchemeParseResults, sanitizedUrl, decodedUrl;
		if (!targetURL) {
			return blankValue;
		}
		sanitizedUrl = String(targetURL)
			.replace(/[^\x20-\x7E]/gim, '')
			.replace(/[^-A-Za-z0-9+&@#/%?=~_|!:,.;\(\){}']+/g, '')
			.trim();
		try {
			decodedUrl = decodeURI(sanitizedUrl);
		} catch (error) {
			// malformed URI
			return blankValue;
		}
		if (/<script/im.test(decodedUrl)) {
			return blankValue;
		}
		urlSchemeParseResults = sanitizedUrl.match(/^([^:]+):/gm);
		if (!urlSchemeParseResults) {
			return sanitizedUrl;
		}
		urlScheme = urlSchemeParseResults[0];
		if (/^(%20|\s)*(javascript|data)/im.test(urlScheme)) {
			return blankValue;
		}
		return sanitizedUrl;
	};

	/**
	 * Normalize a url for comparison later. Strips host, lowercase, removes default index.html
	 * Used for comparing local URLs for equality
	 * @param {*} url url
	 * @return {string}
	 */
	CDC.Common.normalizeUrl = (url) => {
		const defaultFiles = 'index.html|index.htm|default.htm|default.asp|default.html'.split('|');
		const parsed = CDC.Common.parseUrl(url);
		let path = String(parsed.pathname || '').trim();
		let file = '';
		let fileMatch = path.match(/[^\/]+\.[^\/]{2,4}$/);
		if (fileMatch) {
			file = fileMatch[0];
			path = path.replace(/[^\/]+\.[^\/]{2,4}$/, '');
		}
		if (defaultFiles.includes(file.trim().toLowerCase())) {
			file = '';
		}
		return `${path}${file}`.toLowerCase();
	};

	/**
	 * Safe parse a JSON string with optional whitelist array of expected properties
	 *
	 * @name CDC.Common.parseJSON
	 * @param {string} string Input JSON string value
	 * @param {array} props [optional] Array of properties to allow from converted JSON object
	 * @returns {object|null} If JSON is parsed, converted JSON object, otherwise nul
	 */
	CDC.Common.parseJSON = function (string, props) {
		var parsedObj;
		var safeObj = {};
		try {
			parsedObj = $.parseJSON(String(string));
			if ('object' !== typeof parsedObj || !Array.isArray(props)) {
				safeObj = parsedObj;
			} else {
				// copy only expected properties to the safeObj
				props.forEach(function (prop) {
					if (parsedObj.hasOwnProperty(prop)) {
						safeObj[prop] = parsedObj[prop];
					}
				});
			}
			return safeObj;
		} catch (e) {
			console.info("can't parse JSON string: ", string);
			return null;
		}
	};

	/**
	 * Safe method for opening urls, either in current tab or new tab. If URL isn't safe, no action is taken.
	 *
	 * @name CDC.Common.open
	 * @param {string} targetURL URL to open
	 * @param {string} targetWindow [optional] Target tab to open up in.
	 * @example
	 * CDC.Common.open( 'test.html', '_blank' );
	 */
	CDC.Common.open = function (targetURL, targetWindow) {
		targetURL = CDC.Common.cleanUrl(targetURL, false);
		if (!targetURL) {
			console.error('URL is blank. ', targetURL);
			return;
		}
		if (targetWindow) {
			//eslint-disable-next-line
			var target = typeof targetWindow ? targetWindow : null;
			window.open(targetURL, target);
		} else {
			location.href = targetURL;
		}
	};

	/**
	 * Loads a JS script, and runs an optional callback once loaded
	 * @name CDC.Common.loadScript
	 * @param {string|array} scripts  Script or Scripts to load (in order)
	 * @param {function}     callback [optional] Function to callback after JS is loaded
	 */
	CDC.Common.loadScript = function (scripts, callback) {
		if (!Array.isArray(scripts)) {
			scripts = [scripts];
		}
		if (!scripts.length) {
			callback();
			return;
		}
		var script = scripts.shift();
		var eleScript = document.createElement('script'), // NEW SCRIPT TAG
			eleHead = document.getElementsByTagName('head')[0]; // FIRST SCRIPT TAG IN CALLING PAGE

		// LOAD IF SCRIPT VALID ARGUMENT PASSED
		script = CDC.Common.cleanUrl(script, false);
		if (script && 0 < script.length) {
			// SET SCRIPT TAG ATTRIBUTES
			eleScript.src = script; // set the src of the script to your script
			var fctLocalCallback = function () {
				// LOGGING
				// if more scripts to load, continue loading
				if (scripts.length) {
					CDC.Common.loadScript(scripts, callback);
					return;
				}

				// CALLBACK PASSED?
				if (callback !== undefined) {
					// LOG & EXECUTE CALLBACK
					return callback();
				}
			};

			// BIND THE EVENT TO THE CALLBACK FUNCTION
			if (eleScript.addEventListener) {
				eleScript.addEventListener('load', fctLocalCallback, false); // IE9+, Chrome, Firefox
			} else if (eleScript.readyState) {
				eleScript.onreadystatechange = fctLocalCallback; // IE8
			}

			// APPEND SCRIPT TO PAGE
			eleHead.appendChild(eleScript);
		}
	};

	/**
	 * Alias of CDC.Common.loadScript
	 * @name CDC.Common.loadJS
	 * @alias CDC.Common.loadScript
	 */
	CDC.Common.loadJS = CDC.Common.loadScript;

	CDC.Common.typeof = function (data) {
		if (Array.isArray(data)) {
			return 'array';
		}
		return typeof data;
	};

	CDC.Common.toArray = (value) => {
		if (!Array.isArray(value)) {
			if (undefined === value || null === value) {
				return [];
			}
			return [value];
		}
		return value;
	};

	/**
	 * Dynamically load a CSS file from the current domain.
	 *
	 * @name CDC.Common.loadCss
	 * @param {string|array} stylesheetPaths Path or Paths to CSS file(s)
	 * @param {string}       media           Media to apply styles to, default 'print,screen'
	 */
	CDC.Common.loadCss = function (stylesheetPaths, media) {
		if (!Array.isArray(stylesheetPaths)) {
			stylesheetPaths = [stylesheetPaths];
		}
		stylesheetPaths.forEach(function (stylesheetPath) {
			var link = document.createElement('link'),
				hostname = CDC.Common.getSafeHostName(),
				path = CDC.Common.parseUrl(stylesheetPath).pathname;
			link.href = '//' + hostname + path;
			link.type = 'text/css';
			link.rel = 'stylesheet';
			link.media = CDC.Common.cleanAttr(media || 'print,screen');
			document.getElementsByTagName('head')[0].appendChild(link);
		});
	};

	/**
	 * Alias of CDC.Common.loadCss
	 * @name CDC.Common.loadCSS
	 * @alias CDC.Common.loadCss
	 */
	CDC.Common.loadCSS = CDC.Common.loadCss;

	/**
	 * Strips new lines from a string
	 *
	 * @name CDC.Common.cleanString
	 * @param {string} anyString
	 * @returns {string} String stripped of unwanted characters
	 */
	CDC.Common.cleanString = (anyString) => {
		// DEFAULT STRING
		anyString = String(anyString || '');

		// CLEAN IT UP & RETURN IT
		return anyString.replace('\t', '').replace('\r', '').replace('\n', '');
	};

	/**
	 * Generates a randomized 4 character hexadecimal string
	 * @name CDC.Common.s4
	 * @returns {string}
	 */
	CDC.Common.s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);

	// GUID GENERATOR
	/**
	 * Generates a randomized 36 character string with hexadecimal characters and dashes
	 * @name CDC.Common.guid
	 * @returns {string}
	 */
	CDC.Common.guid = function () {
		return (
			CDC.Common.s4() +
			CDC.Common.s4() +
			'-' +
			CDC.Common.s4() +
			'-' +
			CDC.Common.s4() +
			'-' +
			CDC.Common.s4() +
			'-' +
			CDC.Common.s4() +
			CDC.Common.s4() +
			CDC.Common.s4()
		);
	};

	// REPLACE ALL HANDLER
	CDC.Common.replaceAll = function (find, replace, str) {
		if ('|' === find) {
			find = new RegExp('\\|', 'g');
		} else {
			find = new RegExp(find, 'g');
		}
		return str.replace(find, replace);
	};

	/**
	 * Sanitized method for getting the current page's hostname
	 * @name CDC.Common.getSafeHostName
	 * @returns {string} Current page's hostname
	 */
	CDC.Common.getSafeHostName = function () {
		var safeHost = CDC.Common.parseUrl().host;
		var inputHost = CDC.Common.getCallParam('cHost') || CDC.Common.getCallParam('host') || false;
		if (inputHost) {
			inputHost = CDC.Common.parseUrl('//' + inputHost).hostname;
			if (inputHost.match(/\.cdc\.gov$/i)) {
				safeHost = inputHost;
			}
		}
		return safeHost;
	};

	/**
	 * Test if url or local environment is WCMS
	 * @name CDC.Common.isWCMS
	 * @returns {bool}
	 */
	CDC.Common.isWCMS = (url) => {
		url = String(undefined === url ? window.location.href : url).trim();
		if (!url) {
			return false;
		}
		const host = CDC.parseUrl(url).host;
		if (!host) {
			return false;
		}
		// first check, allow local or vvv
		if (host.match(/^(vvv|localhost)/i)) {
			return true;
		}
		// now must be cdc.gov tld
		const match = host.match(/^(.*)\.cdc\.gov$/)
		if (!match) {
			return false;
		}
		const subdomain = match[1];
		// check subdomain
		if (subdomain.match(/(^wcms-wp|^www\b|wwwdev|wwwlink|^atsdr)/i)) {
			return true;
		}
		return false;
	}

	/**
	 * Break a given url into its child parts
	 * _(via: https://www.abeautifulsite.net/parsing-urls-in-javascript)_
	 * @name CDC.Common.parseUrl
	 * @param {string} targetURL [optional] URL to parce, default is the current location href
	 * @returns {{searchObject, protocol: string, hostname: string, search: string, port: string, host: string, hash: string, pathname: string}}
	 */
	CDC.Common.parseUrl = function (targetURL) {
		var parser = document.createElement('a'),
			searchObject = {},
			queries,
			split,
			i;
		// Let the browser do the work
		parser.href = CDC.Common.cleanUrl(targetURL || location.href, '');
		// Convert query string to object
		queries = parser.search.replace(/^\?/, '').split('&');
		for (i = 0; i < queries.length; i++) {
			split = queries[i].split('=');
			searchObject[split[0]] = 2 <= split.length ? split[1] : '';
		}
		// IE fix for pathname - misses leading slash
		var pathname = String(parser.pathname);
		if ('/' !== pathname.charAt(0)) {
			pathname = '/' + pathname;
		}
		return {
			protocol: parser.protocol,
			host: parser.host,
			hostname: parser.hostname,
			port: parser.port,
			pathname: pathname,
			search: parser.search,
			searchObject: searchObject,
			params: searchObject,
			hash: parser.hash,
		};
	};

	// return a random 5 char alphanumeric string
	CDC.Common.getHash = () => Math.floor((1 + Math.random()) * 0x10000).toString(16);

	/**
	 * Checks if url is a cdc.gov domain
	 * @name CDC.Common.cdcUrl
	 * @param targetURL
	 * @returns {boolean}
	 */
	CDC.Common.cdcUrl = function (targetURL) {
		var parts = CDC.Common.parseUrl(targetURL);
		var host = parts.hostname.toLowerCase();
		return 'cdc.gov' === host || 'localhost' === host || '127.0.0.1' === host || RegExp('.cdc.gov$').test(host) || RegExp('.wcms$').test(host);
	};

	// LOCAL STORAGE API HELPER
	/**
	 * Local storage helper object
	 * @name CDC.Common.getLocalStorageApi
	 * @param {string} storeName Name of value in localStorage to work with
	 * @returns {Object}
	 */
	CDC.Common.getLocalStorageApi = function (storeName) {
		var localStorageName = storeName;

		var api = {
			val: function () {
				try {
					if ('undefined' !== typeof window.localStorage) {
						var localStore = window.localStorage[localStorageName];
						if (localStore) {
							return JSON.parse(localStore);
						}
					}
				} catch (e) {
					// localStorage is in the browser, but not available for this site.
				}
				return undefined;
			},
			save: function (anyValue) {
				api.valueType = typeof anyValue;
				if ('object' === api.valueType) {
					if ('[object Array]' === Object.prototype.toString.call(anyValue)) {
						api.valueType = 'array';
					}
				}
				try {
					if ('undefined' !== typeof window.localStorage) {
						window.localStorage[localStorageName] = JSON.stringify(anyValue);
					}
				} catch (e) {
					// localStorage is in the browser, but not available for this site.
				}
			},
			clear: function () {
				try {
					if ('undefined' !== typeof window.localStorage) {
						window.localStorage.removeItem(localStorageName);
					}
				} catch (e) {
					// localStorage is in the browser, but not available for this site.
				}
			},
		};

		return api;
	};

	/**
	 * Creates a shallow copy of a given native object
	 * @name CDC.Common.cloneShallow
	 * @param {any} obj Native object to clone
	 * @returns {any} Copy of the given object
	 */
	CDC.Common.cloneShallow = function (obj) {
		var anyReturn = null;
		switch (CDC.Common.typeof(obj)) {
			case 'array':
				anyReturn = obj.slice(0);
				break;
			case 'object':
				anyReturn = Object.assign({}, obj);
				break;
			default:
				anyReturn = obj;
				break;
		}
		return anyReturn;
	};

	/**
	 * Creates a deep copy of a given native object
	 * @name CDC.Common.cloneDeep
	 * @param {any} obj Native object to clone
	 * @returns {any} Copy of the given object
	 */
	CDC.Common.cloneDeep = function (anyVar, safeCopy) {
		if ('undefined' === typeof safeCopy) {
			safeCopy = true;
		}

		var anyReturn = null;

		switch (CDC.Common.typeof(anyVar)) {
			case 'object':
				anyReturn = {};
				var key;
				for (key in anyVar) {
					if (anyVar.hasOwnProperty(key) || !safeCopy) {
						anyReturn[key] = CDC.Common.cloneDeep(anyVar[key]);
					}
				}
				break;

			case 'array':
				anyReturn = anyVar.slice(0);
				break;

			default:
				anyReturn = anyVar;
				break;
		}
		return anyReturn;
	};

	/**
	 * Merge two objects to their first level of properties
	 * @name CDC.Common.mergeShallow
	 * @param {object} obj1 Object to merge
	 * @param {object} obj2 Second object to merge
	 * @returns {object} A merged object
	 */
	CDC.Common.mergeShallow = function (obj1, obj2) {
		return Object.assign(CDC.Common.cloneShallow(obj1), CDC.Common.cloneShallow(obj2));
	};

	// DATE DIFF METHODS
	CDC.Common.dateDiff = {
		/**
		 * Get difference between two date objects in days
		 * @name CDC.Common.dateDiff.inDays
		 * @param {Date} d1 Date 1
		 * @param {Date} d2 Date 2
		 * @returns {number} Difference in days
		 */
		inDays: function (d1, d2) {
			var t2 = d2.getTime();
			var t1 = d1.getTime();
			return parseInt((t2 - t1) / (24 * 3600 * 1000));
		},
		/**
		 * Get difference between two date objects in weeks
		 * @name CDC.Common.dateDiff.inWeeks
		 * @param {Date} d1 Date 1
		 * @param {Date} d2 Date 2
		 * @returns {number} Difference in weeks
		 */
		inWeeks: function (d1, d2) {
			var t2 = d2.getTime();
			var t1 = d1.getTime();
			return parseInt((t2 - t1) / (24 * 3600 * 1000 * 7));
		},
		/**
		 * Get difference between two date objects in months
		 * @name CDC.Common.dateDiff.inMonths
		 * @param {Date} d1 Date 1
		 * @param {Date} d2 Date 2
		 * @returns {number} Difference in months
		 */
		inMonths: function (d1, d2) {
			var d1Y = d1.getFullYear();
			var d2Y = d2.getFullYear();
			var d1M = d1.getMonth();
			var d2M = d2.getMonth();
			return (d2M + 12) * d2Y - (d1M + 12) * d1Y;
		},
		inYears: function (d1, d2) {
			return d2.getFullYear() - d1.getFullYear();
		},
	};

	/**
	 * Given a url with query string as an object
	 * @name CDC.Common.parseQueryString
	 * @param {string} strUrl URl with querystring
	 * @return {object} Parsed query string
	 */
	CDC.Common.parseQueryString = function (strUrl) {
		var objReturn = {};

		strUrl = 0 === strUrl.indexOf('?') ? strUrl.substring(1) : strUrl;

		if (strUrl.length) {
			var aryCallParams = strUrl.split('&');
			var len = aryCallParams.length;
			while (len--) {
				var aryNvp = aryCallParams[len].split('=');
				objReturn[aryNvp[0]] = aryNvp[1];
			}
		}

		return objReturn;
	};

	/**
	 * Render a number with thousandths commas
	 * @name CDC.Common.numberWithCommas
	 * @param {string|number} number Number to return as a comma'd string
	 * @returns string Number with commas
	 */
	CDC.Common.numberWithCommas = function (number) {
		return String(number).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
	};

	// SAFE CALL PARAMETER RETREIVAL METHOD
	CDC.Common.getCallParam = (function () {
		// SET RUNTIME CALLPARAMS TO THAT OF CALLING PAGS LOCATION URL (THIS IS WHERE MOST REQUESTS WILL COME FROM)
		if (!CDC.Common.runtime.callParams) {
			CDC.Common.runtime.callParams = CDC.Common.parseQueryString(window.location.search);
		}

		return function (paramName, blnDecode, strUrl) {
			blnDecode = 'undefined' === typeof blnDecode ? true : blnDecode;
			var objParams = strUrl ? CDC.Common.parseQueryString(strUrl) : CDC.Common.runtime.callParams;
			var anyVar = objParams[paramName] || null;
			return blnDecode && null !== anyVar ? decodeURIComponent(anyVar) : anyVar;
		};
	})();

	// Standard Query getParam
	// getCallParam doesn't uridecode results
	/**
	 * Fetch a query string parameter from the current page by name
	 * @name CDC.Common.getParam
	 * @param {string} name Name of query param to fetch
	 * @returns {string|null} Value of query param if found, or null
	 */
	CDC.Common.getParam = function (name) {
		var url = window.location.href;
		name = name.replace(/[\[\]]/g, '\\$&');
		var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
			results = regex.exec(url);
		if (!results) {
			return null;
		}

		if (!results[2]) {
			return '';
		}
		return decodeURIComponent(results[2].replace(/\+/g, ' ')).replace(/[<>]/g, '');
	};

	/**
	 * Fetch a query parameter as a boolean switch
	 * ?<param>    true
	 * ?<param>=0  false
	 * ?<param>=y  true
	 * ?<param>=n  false
	 * @name CDC.Common.getParam
	 * @param {string} name          Name of query param to fetch
	 * @param {boolean} defaultValue Default value to return when no param found
	 * @returns {boolean} Switch value
	 */
	CDC.Common.getParamSwitch = function (name, defaultValue) {
		var param = CDC.Common.getParam(name);
		var value = false;
		if ('string' !== typeof param) {
			return Boolean(defaultValue);
		}
		if ('' === param) {
			return true;
		}
		param = String(param).trim().toLowerCase();
		if (param.match(/^\d+$/)) {
			value = Boolean(parseInt(param, 10));
		} else if (param.match(/^(n|no|f|false|off)$/)) {
			value = false;
		} else {
			value = true;
		}
		return value;
	};

	// DEBOUNCE FUNCTION
	CDC.Common.debounce = function (func, wait, immediate) {
		var timeout;
		return function () {
			var context = this,
				args = arguments;
			var later = function () {
				timeout = null;
				if (!immediate) {
					func.apply(context, args);
				}
			};
			var callNow = immediate && !timeout;
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
			if (callNow) {
				func.apply(context, args);
			}
		};
	};

	// Does 'something' when user stops doing an event (scroll, click, resize, etc)
	CDC.Common.debouncer = (func, delay) => {
		let debounceTimer
		return function () {
			const context = this;
			const args = arguments;
			clearTimeout(debounceTimer);
			debounceTimer = setTimeout(() => func.apply(context, args), delay)
		}
	};

	// Does 'something' every specified time
	CDC.Common.throttle = (callback, delay) => {
		let throttleTimer;
		if (throttleTimer) return;
		throttleTimer = true;
		setTimeout(() => {
			callback();
			throttleTimer = false;
		}, delay);
	};

	/**
	 * String HTML tags from a string
	 * @name CDC.Common.stripTags
	 * @param {string} input String to clean
	 * @param {array} allowed Array of allowed tags
	 * @returns {string} String stripped of tags
	 */
	CDC.Common.stripTags = function (input, allowed) {
		allowed = (
			String(allowed || '')
				.toLowerCase()
				.match(/<[a-z][a-z0-9]*>/g) || []
		).join(''); // making sure the allowed arg is a string containing only tags in lowercase (<a><b><c>)
		var tags = /<\/?([a-z][a-z0-9]*)\b[^>]*>/gi,
			commentsAndPhpTags = /<!--[\s\S]*?-->|<\?(?:php)?[\s\S]*?\?>/gi,
			brokenTags = /(<\w+(?:\s+\w+=\"[^"]+\")*)(?=[^>]+(?:<|$))/g;
		return String(input)
			.replace(commentsAndPhpTags, '')
			.replace(brokenTags, '')
			.replace(tags, function ($0, $1) {
				return -1 < allowed.indexOf('<' + $1.toLowerCase() + '>') ? $0 : '';
			});
	};

	/**
	 * Return string in TitleCase
	 * @name CDC.Common.titleCase
	 * @param {string} string String to convert
	 * @returns {string} TitleCase string
	 */
	CDC.Common.titleCase = function (string) {
		return String(string)
			.toLowerCase()
			.split(' ')
			.map(function (word) {
				return word.charAt(0).toUpperCase() + word.slice(1);
			})
			.join(' ');
	};

	/**
	 * Return string capitalized
	 * @name CDC.Common.capitalize
	 * @param {string} string String to convert
	 * @returns {string} capitalized string
	 */
	CDC.Common.capitalize = function (string) {
		return String(string).charAt(0).toUpperCase() + String(string).slice(1);
	};

	/**
	 * Diff 2 arrays
	 * @name Returns an array with elements from array b removed from array a
	 * @param {array} a Source array
	 * @param {array} b Target array to remove from source array
	 * @returns {array} Array a with items in array b removed
	 */
	CDC.Common.arrayDiff = function (a, b) {
		if (!Array.isArray(a)) {
			return [];
		}
		if (!Array.isArray(b)) {
			b = [b];
		}
		var c = a.slice();
		$.each(b, function (i, term) {
			var index = c.indexOf(term);
			if (-1 < index) {
				c.splice(index, 1);
			}
		});
		return c;
	};

	/**
	 * Returns an array with all duplicate items removed
	 * @name CDC.Common.unique
	 * @param {array} array Input array
	 * @returns {array} Array with duplicates removed
	 */
	CDC.Common.unique = function (array) {
		if (!Array.isArray(array)) {
			return [];
		}
		array = array.filter(function (el) {
			return Boolean(el);
		});
		return array.filter(function (el, index, arr) {
			return index === arr.indexOf(el);
		});
	};

	/**
	 * Alias of CDC.Common.unique
	 * @name CDC.Common.arrayUnique
	 * @alias CDC.Common.unique
	 */
	CDC.Common.arrayUnique = CDC.Common.unique;

	/**
	 * Left pad a string with leading chars
	 *
	 * @param string  Input string
	 * @param size    Final length of string, default = 2
	 * @param padding Default is '0'
	 * @returns {string}
	 */
	CDC.Common.lpad = function (string, size, padding) {
		string = String(string);
		padding = padding ? String(padding).charAt(0) : '0';
		size = size || 2;
		while (string.length < size) {
			string = padding + string;
		}
		return string;
	};

	/**
	 * Return boolean based on whether or not the hostname is in the development environments
	 * @name CDC.Common.isProd
	 * @returns {Boolean}
	 */
	CDC.Common.isProd = function () {
		return !CDC.parseUrl().hostname.match(/local|vvv|dev|test|stage|prototype/);
	};

	/**
	 * Compares two software version string
	 *
	 * @name CDC.Common.compareVersion
	 * @param {string} v1 Version 1
	 * @param {string} v2 Version 2
	 * @returns {false|integer} False if no comparison can be made, -1|0|1 if comparison made
	 */
	CDC.Common.compareVersion = function (v1, v2) {
		if ('string' !== typeof v1) return false;
		if ('string' !== typeof v2) return false;
		v1 = v1.split('.');
		v2 = v2.split('.');
		const k = Math.min(v1.length, v2.length);
		for (let i = 0; i < k; ++i) {
			v1[i] = parseInt(v1[i], 10);
			v2[i] = parseInt(v2[i], 10);
			if (v1[i] > v2[i]) return 1;
			if (v1[i] < v2[i]) return -1;
		}
		if (v1.length === v2.length) {
			return 0;
		}
		return (v1.length < v2.length) ? -1 : 1;
	};

	// jQuery "safe" overrides for sanitizing HTML
	// clean any HTML before injecting into the page
	if (window.$ && window.$.fn) {
		$.fn.safehtml = function () {
			var args = arguments;
			if (args.length && 'string' === typeof args[0]) {
				// here we're cleaning the set HTML from XSS vulnerabilities
				args[0] = CDC.Common.cleanHTML(args[0]);
			}
			return $.fn.html.apply(this, args);
		};

		// same, cleaning HTML
		$.fn.safeappend = function () {
			var args = arguments;
			if (args.length && 'string' === typeof args[0]) {
				// here we're cleaning the set HTML from XSS vulnerabilities
				args[0] = CDC.Common.cleanHTML(args[0]);
			}
			return $.fn.append.apply(this, args);
		};
	}

	// Store path to TP root, fetched from first /TemplatePackage script
	CDC.tpPath = (function(){
		var scripts = document.getElementsByTagName('script');
		for ( var i = 0; i < scripts.length; i++ ) {
			var src = String(scripts[i].getAttribute('src'));
			if ( -1 < src.indexOf( '/TemplatePackage') ) {
				return String(src).replace(/\/TemplatePackage\/.*/, '')
			}
		}
		return '';
	})();

	CDC.Common.isElement = function(node) {
		if ('object' !== typeof (node)) {
			return false;
		}
		return node && node.nodeType && node.nodeType === Node.ELEMENT_NODE;
	}

	/**
	 * Make an HTML Element
	 * @param {string} tagName tag name of element to make
	 * @param {string|array} classNames class / list of classes to add
	 * @param {object} attributes element attributes
	 * @param {string|HTMLElement} content content inside new element
	 * @returns
	 */
	CDC.Common.make = function(tagName, classNames = '', attributes = {}, content) {
		const el = document.createElement(tagName);
		// merge all classnames and split by whitespace
		let flatClassNames = String( Array.isArray(classNames) ? classNames.join(' ') : classNames ).trim();
		if (flatClassNames) {
			classNames = flatClassNames.split(/\s+/);
			el.classList.add(...classNames);
		}
		if ('object' === typeof attributes) {
			for (const attrName in attributes) {
				el[attrName] = attributes[attrName];
				el.setAttribute(attrName, attributes[attrName]);
			}
		};
		if (content) {
			if (CDC.Common.isElement(content)) {
				el.append(content);
			} else {
				el.innerHTML = content;
			}
		}
		return el;
	};
	CDC.Common.getCookie = function( cookieName ) {
		let name = cookieName + '=';
		let decodedCookie = decodeURIComponent(document.cookie);
		let cookieArray = decodedCookie.split(';');
		for (let i = 0; i < cookieArray.length; i++) {
			let cookie = cookieArray[i].trim();
			if (0 === cookie.indexOf(name)) {
				return cookie.substring(name.length, cookie.length);
			}
		}
		return null;
	};

	// Grab /config/cdc_config.js values from WCMS
	CDC.config = Object.assign({}, window.CDC_WEB_CONFIG, window.CDC_CONFIG);

	// Add aliases
	CDC.isProd = CDC.Common.isProd;
	CDC.getParam = CDC.Common.getParam;
	CDC.open = CDC.Common.open;
	CDC.parseUrl = CDC.Common.parseUrl;
	CDC.cleanUrl = CDC.Common.cleanUrl;
	CDC.cleanHTML = CDC.Common.cleanHTML;
	CDC.cleanAttr = CDC.Common.cleanAttr;
	CDC.debug = CDC.Common.getParamSwitch('cdcdebug', false);
	CDC.make = CDC.Common.make;
	CDC.getCookie = CDC.Common.getCookie;
	// finally load DOMPurify script if it's not available
	if ('function' !== typeof window.DOMPurify) {
		CDC.Common.loadScript('https://www.cdc.gov/TemplatePackage/contrib/libs/dompurify/latest/purify.min.js');
	}
})();

// Simple event emitter
class CDCEvents {

	// private array of all event listeners
	_events = {};
	// private array of all queued once event listeners
	_queues = {};
	// private array of listeners that fire on every event
	_all = [];
	// events that only run once, so later hooks trigger on attach
	RUNONCE_EVENTS = ['init', 'ready', 'navLoaded'];

	// past events
	_pastEvents = [];

	constructor() {}

	/**
	 * Watch for a specific event
	 * @param {string|array} eventName Name of event(s) to watch
	 * @param {function} callback Callback function to execute
	 */
	on(eventName, callback) {
		if ('function' !== typeof callback) {
			return;
		}
		if (Array.isArray(eventName)) {
			eventName = eventName.join(' ');
		}
		let eventNames = CDC.Common.cleanString(eventName).trim().split(/[ ,]+/);
		eventNames.forEach(name => {
			name = CDC.Common.cleanString(name);
			if (!name) {
				return
			}
			if (!this._events[name]) {
				this._events[name] = [];
			}
			// special case: event 'now' runs immediately
			if ('now' === name) {
				return callback();
			}
			this._events[name].push(callback);
			// special case: init or ready event, if already ran - trigger callback
			if (this.RUNONCE_EVENTS.includes(name) && this._pastEvents.includes(name)) {
				return callback();
			}
		});
	}

	/**
	 * Fire a callback on the next fire of an event
	 * @param {string|array} eventName Name of event(s) to watch
	 * @param {function} callback Callback function to execute
	 */
	once(eventName, callback) {
		if (Array.isArray(eventName)) {
			eventName = eventName.join(' ');
		}
		let eventNames = CDC.Common.cleanString(eventName).trim().split(/[ ,]+/);
		eventNames.forEach(name => {
			name = CDC.Common.cleanString(name);
			if (!name) {
				return
			}
			if (!this._queues[name]) {
				this._queues[name] = [];
			}
			this._queues[name].push(callback);
		});
	}

	/**
	 * A call back to run on all events
	 * @param {function} callback Callback function to execute
	 *   Format of callback has 2 arguments
	 *    - {string} eventName Name of event called
	 *    - {mixed} data Any data sent from emitter
	 */
	onAll(callback) {
		this._all.push(callback);
	}

	/**
	 * Trigger an event
	 * @param {string} eventName Name of event to emit
	 * @param {mixed} data [optional] Additional param to send along
	 */
	emit(eventName, data) {
		eventName = CDC.Common.cleanString(eventName);
		if (!eventName) {
			return eventName;
		}
		if (Array.isArray(this._events[eventName])) {
			this._events[eventName].forEach(method => {
				if ('function' === typeof method) {
					method(data);
				}
			});
		}
		// go through all queued run once events
		if (Array.isArray(this._queues[eventName])) {
			this._queues[eventName].forEach(method => {
				if ('function' === typeof method) {
					method(data);
				}
			});
			this._queues[eventName] = [];
		}
		// call any "always" events with event name
		if (Array.isArray(this._all)) {
			this._all.forEach(method => {
				if ('function' === typeof method) {
					// these get eventName first, then optional param
					method(eventName, data);
				}
			});
		}
		// add to pastEvents
		this._pastEvents.push(eventName)
	}
}

/**
 * General Modal helper class
 */
class CDCModal {

	// dom element for modal
	element;
	// various dom nodes for reference
	nodes = {};

	// bootstrap modal class
	modal;

	// is open
	isOpen = false;

	// individual config
	config = {};

	// default modal configuration all start with
	static defaultConfig = {
		open: true,
		title: 'Notice',
		className: [],
		id: null,
		size: '',
		message: '',
		buttons: [
			{
				text: 'Close',
				className: 'btn-secondary',
			}
		]
	}

	// default button configuration
	static buttonConfig = {
		text: '',
		className: '',
		closeOnClick: true,
		onClick: null,
	};

	constructor(config) {
		config = Object.assign({}, CDCModal.defaultConfig, config);
		this.config = config;
		if (!config.id) {
			config.id = `modal-${CDC.Common.getHash()}`;
		}
		let classNames = ['modal','fade'];
		if (config.className) {
			if (Array.isArray(config.className)) {
				classNames = classNames.concat(config.className);
			} else {
				classNames.push(config.className);
			}
		}
		this.element = CDC.Common.make('div', classNames.join(' '), {id: config.id, 'aria-labelledby': `${config.id}-title`, 'aria-hidden': true, tabindex:-1},
		`
			<div class="modal-dialog ${config.size}">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title" id="${config.id}-title"></h5>
						<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"><span class="cdc-icon-close"></span></button>
					</div>
					<div class="modal-body">
					</div>
					<div class="modal-footer">
					</div>
				</div>
			</div>
		`);
		document.body.append(this.element);
		this.nodes = {
			header: this.element.querySelector('.modal-header'),
			title: this.element.querySelector('.modal-title'),
			body: this.element.querySelector('.modal-body'),
			footer: this.element.querySelector('.modal-footer'),
		};
		this.nodes.title.innerHTML = CDC.Common.cleanHTML((config.title || '').trim());
		this.nodes.body.innerHTML = CDC.Common.cleanHTML(String(config.message || '').trim());

		// build buttons
		if (Array.isArray(this.config.buttons)) {
			this.config.buttons.forEach(buttonConfig => {
				buttonConfig = Object.assign({}, CDCModal.buttonConfig, buttonConfig);
				let buttonClassNames = ['btn'];
				if (Array.isArray(buttonConfig.className)) {
					buttonClassNames = buttonClassNames.concat(buttonConfig.className);
				}
				if ('string' === typeof buttonConfig.className) {
					buttonClassNames.push(buttonConfig.className);
				}
				const buttonElement = CDC.Common.make('button', buttonClassNames, {}, buttonConfig.text);
				if ('function' === typeof buttonConfig.onClick) {
					buttonElement.addEventListener('click', () => buttonConfig.onClick());
				}
				if (buttonConfig.closeOnClick) {
					buttonElement.addEventListener('click', () => this.close());
				}
				this.nodes.footer.append(buttonElement);
			})
		}

		this.modal = new bootstrap.Modal(this.element);

		this.element.addEventListener('shown.bs.modal', () => {
			this.isOpen = true;
			// @TODO: optionally add onShow method and config
		});
		this.element.addEventListener('hidden.bs.modal', () => {
			this.isOpen = false;
			// @TODO: optionally add onHide method and config
		});

		if (config.open) {
			this.modal.show();
		}
	}

	show() {
		this.modal.show();
	}
	open() {
		this.modal.show();
	}
	hide() {
		this.modal.hide();
	}
	close() {
		this.modal.hide();
	}
}

/**
 * Logic for emailforms
 */
class CDCForms {
	constructor(formSelector) {
		this.form = document.querySelector(formSelector);
		if (!this.form) {
			return;
		}
		this.initialize();
	}

	initialize() {
		this.setupSelectMenus();
	}

	setupSelectMenus() {
		const selectElements = this.form.querySelectorAll('select.form-control');

		selectElements.forEach(select => {
			if (!select.hasAttribute('multiple')) {
				select.setAttribute('data-status', 'closed');
				this.addEventListeners(select);
			}
		});
	}

	addEventListeners(select) {
		select.addEventListener('focus', () => {
			select.setAttribute('data-status', 'open');
		});

		select.addEventListener('blur', () => {
			select.setAttribute('data-status', 'closed');
		});

		// this logic isn't great. Tried click as well, just losing focus from a select isn't without issue
		document.addEventListener('mousedown', (event) => {
			if (!select.contains(event.target) && select.getAttribute('data-status') === 'open') {
				select.setAttribute('data-status', 'closed');
			}
		});
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const cdcForms = new CDCForms('.cdcemailform');
});

/**
 * Logic for common page features like accordions, popovers, etc.
 */
class CDCFeatures {
	accordions = [];
	popovers = [];

	constructor() {
		this.init();
	}

	init() {
		this.loadPopovers();
		this.handleReferences();
		this.handleClipboardBtns();
		this.audioLengthUpdate();
		this.handleSocialSharing();
		this.handleOTPPosition();
		this.handleOTPShowMore();
		this.loadAccordions();
		// site alert for prototype
		this.loadBannerAlert();
		this.fixSSIerrors();
		this.loadQRCode();
		this.handleExternalLinksModal();
		this.handleViewLargerLinksModal();
		this.toggleContentFinder();
		this.toggleTextDescriptionFinder();
		this.curatedLinkShowDownloadColumn();
		this.wideBlockLayoutHandler();
		this.ytPrintLinkHandler();
		this.handleEmailForms();
		this.handleSensitiveImages();
		this.printLink();
		this.tableScrollHandler();
	}

	// logic for accordions
	loadAccordions() {
		var translateShowMore = CDC_Lang.__('Expand All');
		var translateShowLess = CDC_Lang.__('Collapse All');
		$('main .accordions ').each(function () {
			let accordionTitle = $(this).parent().find('h2').first();

			if (accordionTitle.hasClass('accordion-header')) {
				return;
			}

			// Create a div with the class 'accordion-title'
			let accordionTitleDiv = $('<div class="accordion-title"></div>');

			// Add the h2 to the div
			accordionTitleDiv.append(accordionTitle);

			// Add the a link after the div
			accordionTitleDiv.append('<span><a href="#" class="accordion__toggle-all expand-all">' + translateShowMore + '</a></span>');

			// Add the div to the parent
			$(this).parent().prepend(accordionTitleDiv);
		});

		$('main .accordion-title a.accordion__toggle-all ').each(function (i) {
			const $toggle = $(this);
			const $accordionContainer = $toggle.closest('.accordion-title').nextUntil('.accordion-title').filter('.accordions');

			function updateToggleText() {
				const isAnyOpen = $accordionContainer.find('.accordion-collapse.show').length > 0;
				$toggle.text(isAnyOpen ? translateShowLess : translateShowMore);
				$toggle.toggleClass('collapse-all', isAnyOpen).toggleClass('expand-all', !isAnyOpen);
			}

			$toggle.addClass(`panel-${i}`).on('click', function () {
				if (translateShowMore === $toggle.text()) {
					$($toggle.parent().parent().next().parent().find('.accordion-header button')).each(function () {
						let btn = $(this);
						btn.removeClass('collapsed');
						btn.attr('aria-expanded', true);
						btn.parent().next('.accordion-collapse').removeClass('collapse').addClass('show');
					});
					// Collapse All text
					$toggle.text(translateShowLess);
					$toggle.removeClass('expand-all');
					$toggle.addClass('collapse-all');
				} else {
					$('button[aria-expanded="true"]').each(function () {
						let btn = $(this);
						btn.addClass('collapsed');
						btn.attr('aria-expanded', false);
						btn.parent().next('.accordion-collapse').addClass('collapse').removeClass('show');
					});
					$toggle.text(translateShowMore);
					$toggle.removeClass('collapse-all');
					$toggle.addClass('expand-all');
				}
				return false;
			});

			// Add event listeners to each accordion
			$accordionContainer.find('.accordion').each(function() {
				$(this).on('shown.bs.collapse hidden.bs.collapse', updateToggleText);
			});

			// Initial text update
			updateToggleText();
		});
	}

	// logic for initializing popovers
	loadPopovers() {
		const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
		if (popovers?.length) {
			this.popovers = popovers.map((popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl));
		}
	}

	audioLengthUpdate() {
		const audioTags = document.getElementsByTagName('audio');
		// you don't look like an HTMLCollection, let's get out of here
		if (!HTMLCollection.prototype.isPrototypeOf(audioTags)) {
			return;
		}

		for (let i = 0; i < audioTags.length; i++) {
			const audio = new Audio();
			audio.preload = 'metadata';
			audio.src = audioTags[i].getElementsByTagName('source')[0].getAttribute('src');
			audio.addEventListener('loadedmetadata', function () {
				const seconds = audio.duration;
				const h = Math.floor(seconds / 3600);
				const m = Math.floor((seconds % 3600) / 60);
				const s = Math.floor(seconds % 60);
				const formattedTime = [h > 0 ? h + ' hours' : 0, m + ' minutes ', s + ' seconds']
					.filter((a) => a)
					.join(' ');
				document.getElementById(audioTags[i].id + '__length').innerText = formattedTime;
				if (s + m + h > 0) {
					const x = document.getElementById(audioTags[i].id + '_length_container');
					x.style.display = 'inline';
				}
			});
		}
	}

	handleReferences() {
		$('main .cdc-references-cite a, main .cdc-footnotes-cite a').on('click', (e) => {
			const id = e.target?.getAttribute('href');
			if (id) {
				e.preventDefault();
				if ($('#content-sources').hasClass('show')) {
					document.querySelector(id)?.scrollIntoView();
				} else {
					$('#content-sources').collapse('show');
					setTimeout(() => {
						document.querySelector(id)?.scrollIntoView();
					}, 400);
				}
			}
		});
	}

	handleSensitiveImages() {
		$('.image-container.sensitive, .dfe-curated-link__image.sensitive').each((i, imageContainer) => {
			let sensitiveContainer = document.createElement('div');
			sensitiveContainer.classList.add('sensitive-image-overlay');

			let innerContainer = document.createElement('div');
			innerContainer.classList.add('sensitive-image-overlay__message-container');

			let message = document.createElement('div');
			message.classList.add('sensitive-image-overlay__message')
			message.innerHTML = CDC_Lang.__('This photo contains content that may be sensitive to some people');

			let button = document.createElement('button');
			button.innerText = CDC_Lang.__('View photo');
			button.classList.add('btn');
			button.classList.add('btn-blue');

			button.addEventListener('click', (e) => {
				e.preventDefault();
				let container = sensitiveContainer.parentElement;
				container.classList.remove('sensitive');
				sensitiveContainer.parentElement.removeChild(sensitiveContainer);
			});

			innerContainer.appendChild(message);
			innerContainer.appendChild(button);
			sensitiveContainer.append(innerContainer);
			imageContainer.append(sensitiveContainer);
		});
	}

	handleEmailForms() {
		$('.dfe-block--email_signup_form form').each((i, form) => {
			form.setAttribute('action', 'https://tools.cdc.gov/campaignproxyservice/subscriptions.aspx');
		});
	}

	handleClipboardBtns() {
		$('[data-clipboard-btn]').each((i, button) => {
			button.addEventListener('click', (e) => {
				e.preventDefault();
				const selector = button.getAttribute('data-clipboard-btn');
				let textChange = button.getAttribute('data-textChange');
				if (!selector) {
					return;
				}
				if (!textChange) {
					textChange = 'Copied';
				}
				const $target = $(selector);
				if (!$target.length || !$target.val()) {
					return;
				}
				const $temp = $('<input>');
				$('body:first').append($temp);
				$temp.val($target.val()).select();
				try {
					document.execCommand('copy');
					button.innerText = textChange;
				} catch (error) {
					console.error('Failed to copy to clipboard:', error);
				}
				$temp.remove();
			});
		});
	}

	handleSocialSharing() {
		var isProd = !window.location.hostname.match(/local|vvv|dev|test|stage|prototype/);
		var title = [$('main h1:first').text(), String(document.title).replace(/\s\|.*/, '')].shift();
		var url = [$('head link[rel="canonical"]').attr('href'), document.location.href].shift();

		// don't share non-prod urls, unless debugging
		url = isProd || CDC.Common.getParamSwitch('cdcdebug') ? url : 'https://www.cdc.gov';
		var props = {
			title: encodeURIComponent(title),
			url: encodeURIComponent(url),
		};
		var socialUrl = '';

		// Facebook
		socialUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + props.url;
		$('.page-share-facebook').attr('href', socialUrl);

		// Twitter
		socialUrl = 'http://twitter.com/share?url=' + props.url + '&text=' + props.title;
		$('.page-share-twitter').attr('href', socialUrl);

		// LinkedIn
		socialUrl = 'https://www.linkedin.com/shareArticle?url=' + props.url + '&title=' + props.title;
		$('.page-share-linkedin').attr('href', socialUrl);
	}

	handleOTPPosition() {
		// TODO: Delete eventually, but saving for reference sakes for now
		// const h2 = $( '#content h2' ).first(),
		// 	otp = $( '.right-rail__static .on-this-page' ).first();
		// 	otp.css( 'margin-top', h2.height() + 36 );		// 36 is the bonus 2rem top

		function initOTPPosition() {
			// Should only work on desktop/lg screen sizes
			if (window.innerWidth < 992) return;

			// `querySelector()` method grabs the first matched element (even when more than one exists)
			const h2 = document.querySelector('#content h2');

			// truthy check... DO NOTHING if there are no h2's
			if (!h2 || h2.length === 0) return;

			// Get the h2's height
			const height = h2.offsetHeight;
			// Get the h2's marginTop value, returns 0 if marginTop is not set
			const computedMarginTop = parseInt(window.getComputedStyle(h2).marginTop);
			const otp = document.querySelector('.page-right-rail__static .on-this-page');

			// truthy check... DO NOTHING if there is no otp
			if (!otp || otp.length === 0) return;

			// Sets the margin-top based on h2's height+marginTop/Bottom computed values
			// 18px is the equivalent of 1rem (18px)
			otp.style.marginTop = `${height + computedMarginTop - 18}px`;
		}

		initOTPPosition(); // init on load
		window.onresize = initOTPPosition; // init on resize
	}

	// show more on On This Page
	handleOTPShowMore() {

		const otp = document.querySelector('.page-right-rail .on-this-page');
		const otpCardBody = otp?.querySelector('.card-body');
		if (!otp) {
			return;
		}
		const linksLimit = (window.innerWidth > 992) ? 10 : 5;
		otp.ul = otp.querySelector('ul');
		otp.links = otp.ul?.querySelectorAll('li');

		// nothing to do if we're under the limit
		if (!otp.ul || otp.links.length <= linksLimit) {
			return;
		}
		otp.isOpen = false;
		otp.button = CDC.make('a', 'more-link', {href:'#'}, CDC_Lang.__('Show More'));
		otpCardBody.append(otp.button);

		otp.toggle = (onoff) => {
			otp.isOpen = (undefined !== onoff) ? !!onoff : !otp.isOpen;
			otp.classList.toggle('open', otp.isOpen);
			otp.button.innerHTML = otp.isOpen ? CDC_Lang.__('Show Less') : CDC_Lang.__('Show More');
			otp.links.forEach((li, index) => {
				if (index >= (linksLimit)) {
					li.classList.toggle('d-none', !otp.isOpen);
				}
			})
		};
		otp.button.addEventListener('click', (e) => {
			e.preventDefault();
			otp.toggle()
		});
		otp.toggle(otp.isOpen);
	}

	// @TODO: address another way
	loadBannerAlert() {
		const siteAlert = document.querySelector('[data-cdc-site-alert]');
		const betaNoticeFlag = CDC.Page?.config?.beta_notice;
		if (siteAlert) {
			if (window.location.hostname.includes('prototype.cdc')) {
				siteAlert.innerHTML = `
					<div class="cdc-site-alert">
						<div class="alert alert-error alert-icon" role="status" aria-live="polite">
							<p><strong>DISCLAIMER:</strong><br/> This page is not for official use and does not represent cleared content. This page is published temporarily and is for user testing purposes only.</p>
						</div>
					</div>
				`;
			} else if ('snapshot2024.cdc.gov' === window.location.hostname) {
				// snapshot banner
				siteAlert.innerHTML = `
					<div class="alert alert-danger my-2 p-2 text-center" role="status" aria-live="polite" style="border:0;color:#000;">
						<div style="max-width:800px; margin: auto">
							This is a complete historical copy of <a href="https://www.cdc.gov">www.cdc.gov</a> as it appeared on May 15 before relaunch. This site will be available through November 2024.
							For the new CDC.gov, visit <b><a href="https://www.cdc.gov">www.cdc.gov</a></b>.
						</div>
					</div>
				`;
			}
		}
	}

	// fix ssi errors
	fixSSIerrors() {
		try {
			// in debug mode, disable
			document.querySelectorAll('B').forEach((element) => {
				if ('Error processing SSI file' === element.innerHTML) {
					if ('BR' === element.nextSibling?.nodeName) {
						element.nextSibling.remove();
					}
					element.remove();
				}
			});
		} catch (e) {
			console.debug('ssi fix stop:', e);
		}
	}

	// Generate QR Code on page for print
	loadQRCode() {
		try {
			CDC.Common.loadJS(CDC.tpPath + '/TemplatePackage/contrib/libs/qrcodejs/latest/qrcode.min.js', function () {
				var pageUrl = CDC.cleanUrl(location.href).replace(/[\?#].*$/, '');
				var qrCodeDiv = $('#cdc-print-qrcode:first');
				if (!qrCodeDiv.length) {
					qrCodeDiv = $('<div id="cdc-print-qrcode" class="d-none d-print-block ms-auto" />').hide();
					$('header.cdc-header').append(qrCodeDiv);
				}

				if (!window.QRCode) {
					console.log('returned');
					return;
				}
				// latest version
				window.QRCode.toDataURL(
					pageUrl + '?s_cid=qr2022',
					{
						errorCorrectionLevel: 'H',
						type: 'image/jpeg',
						quality: 0.3,
						margin: 0,
						scale: 2,
						color: {
							dark: '#000000',
							light: '#ffffff',
						},
					},
					function (err, url) {
						if (!err && url) {
							qrCodeDiv.safeappend($('<img />').attr('src', url)).show();
						}
					}
				);
			});
		} catch (e) {
			console.log('QR Code not loaded', e);
		}
	}

	/**
	 * Show a modal if users click on any external link
	 */
	handleExternalLinksModal() {
		// For now all external links have a similar class
		const links = document.querySelectorAll('.tp-link-policy');

		// Do nothing if no external links then do nothing
		if (!links.length) return;

		links.forEach((link) => {
			link.target = '_blank';
		});
	}

	/**
	 * Get the dimensions of an image from a URL.
	 * @param {string} url - The URL of the image.
	 * @returns {Promise} - A promise that resolves to an object containing the image's width and height.
	 */
	getImageDimensions(url) {
		return new Promise((resolve, reject) => {
			const img = new Image();
			img.onload = () => {
				resolve({ width: img.naturalWidth, height: img.naturalHeight });
			};
			img.onerror = reject;
			img.src = url;
		});
	}

	/**
	 * Show a modal if users click on a view larger image link.
	 * Updates the image dimensions based on the content width and ensures valid width is used.
	 */
	handleViewLargerLinksModal() {
		const links = document.querySelectorAll('span.image-modal a');
		// if no links then do nothing
		if (!links.length) return;
		links.forEach((link) => {
			const dfeImage = link.closest('.dfe-image');
			const image = dfeImage?.querySelector('img');
			const caption = dfeImage?.querySelector('figcaption');
			if (!image) {
				return;
			}
			const imageUrl = image.src;
			this.getImageDimensions(imageUrl)
				.then(dimensions => {
					const msgElement = CDC.make('div');
					const clonedImage = image.cloneNode();
					const content = document.querySelector('#content');
					let imgWidth = '800px';		// default "big" image width, if we cannot figure out content width

					// Check if content exists and get it's width if we need it
					if (content) {
						const tmpWidth = content.getBoundingClientRect().width;
						if ('number' === typeof tmpWidth && 0 < tmpWidth) {
							imgWidth = tmpWidth + 'px';
						}
					}

					// Set min and max styles based on image size
					if (dimensions.width < 660) {
						clonedImage.style.minWidth = '300px';
					} else {
						clonedImage.style.minWidth = '660px';
						clonedImage.style.maxWidth = imgWidth;
					}

					msgElement.append(clonedImage);
					if (caption) {
						msgElement.append(caption.cloneNode(true));
					}
					link.addEventListener('click', (event) => {
						// Hijack default behavior
						event.preventDefault();
						const modal = new CDCModal({
							className: ['modal-view-larger'],
							size: 'modal-lg',
							title: '',
							message: `${msgElement.innerHTML}`,
							buttons: [],
						});
						// Show the modal
						modal.show();
					});
				})
				.catch(error => {
					console.error('Error loading image:', error);
				});
		});
	}

	toggleContent( contentId, link ) {
		let content = document.getElementById(contentId);
		let seeMoreText = link.innerText;
		const translateShowMore = content.dataset?.textOpen ?? CDC_Lang.__('Show More');
		const translateShowLess = content.dataset?.textClose ?? CDC_Lang.__('Show Less');

		let $linkJQuery = $(link);
		if ($linkJQuery.hasClass('closed') || translateShowMore === seeMoreText) {
			// element is closed - now expand the element
			content.style.whiteSpace = 'normal';
			content.innerHTML = content.dataset.originalContent;
			// get the translation for to close (Show Less)
			link.innerHTML = '<span class="cdc-icon cdc-fa-light cdc-fa-angle-up"></span>' + translateShowLess;
			$linkJQuery.removeClass('closed');
			$linkJQuery.addClass('opened');
		} else if ($linkJQuery.hasClass('opened') || translateShowLess === seeMoreText) {
			// element is expanded, now shorten or close the element
			content.innerHTML = content.dataset.truncatedContent + '...';
			//get the translation for to open
			link.innerHTML = '<span class="cdc-icon cdc-fa-light cdc-fa-angle-down"></span>' + translateShowMore;
			$linkJQuery.removeClass('opened');
			$linkJQuery.addClass('closed');
		}
	}

	toggleContentFinder() {
		let ellipsisContents = document.querySelectorAll('[data-toggle-content]');
		ellipsisContents.forEach((item) => {
			// Get Data Value, use it to find ID of content to truncate
			let dataValue = item.getAttribute('data-toggle-content');
			let content = document.getElementById(dataValue);
			let chars = parseInt(item.getAttribute('data-content-chars') || 140);

			// Store Original Content
			content.dataset.originalContent = content?.innerHTML;
			// Truncate Content
			content.dataset.truncatedContent = content?.innerHTML.substring(0,chars).split( /\s(?=\w)/ ).join( ' ' ).replace( /<[^>]+$/, '' );
			content.innerHTML = content.dataset.truncatedContent + '...';
			item.style.display = "block";
			item.addEventListener('click', () => this.toggleContent(dataValue, item) );
		});
	}

	toggleTextDescription(link, id) {
		let item = document.getElementById(id);
		item.classList.toggle('hide');
		if (item.classList.contains('hide')) {
			link.innerHTML = '<span class="cdc-icon cdc-fa-light cdc-fa-angle-down"></span>' + CDC_Lang.__('Show Text Description');
		} else {
			link.innerHTML = '<span class="cdc-icon cdc-fa-light cdc-fa-angle-up"></span>' +  CDC_Lang.__('Hide Text Description');
		}
	}

	toggleTextDescriptionFinder() {
		let textContents = document.querySelectorAll('[data-toggle-text]');
		textContents.forEach((item) => {
			// Get Data Value, use it to find ID of content to truncate
			let dataValue = item.getAttribute('data-toggle-text');
			item.addEventListener('click', () => this.toggleTextDescription(item, dataValue));
		});
	}

	curatedLinkShowDownloadColumn() {
		// Get all the <section> elements on the page
		const sections = document.querySelectorAll('div.dfe-section');
		// Iterate through each section
		sections.forEach((section) => {
			// get all download links
			const downloadDivs = section.querySelectorAll('.dfe-curated-link__download');
			let hasContent = false;

			for (const downloadDiv of downloadDivs) {
				if (downloadDiv.innerHTML.trim().length > 0) {
					hasContent = true;
					break; // Exit the loop
				}
			}

			// if one has content then add .has-content to all within that section
			if (hasContent) {
				downloadDivs?.forEach((downloadDiv) => {
					downloadDiv.classList.add('has-content');
				});
			}

		});
	};

	/**
	 * Handles standard, wide and full_width layouts
	 */
	wideBlockLayoutHandler() {
		// We only care for wide layouts if screen size is > 992
		if (window.innerWidth < 992) return;

		const pageContent = document.querySelector('.cdc-page-content');

		if (!pageContent) return;

		const layouts = ['standard', 'wide', 'full_width']; // the various layouts

		// Observes when the element exists, then move forward with resizing the height
		// Should only run on full_width layouts because the parent is absolutely positioned
		// See _blocks.scss for more info on the CSS
		const handleObserveElement = (element) => {
			const elementObserver = new MutationObserver(() => {
				if (document.contains(element) && element.classList.contains('dfe-block--width-full_width')) {
					handleObserveElementResize(element);
					elementObserver.disconnect();
				}
			});

			elementObserver.observe(document.body, { childList: true, subtree: true });
		};

		// Helps observe elements when they are resized, this happens on render and on click
		const handleObserveElementResize = (element) => {
			const resizeObserver = new ResizeObserver(() => handleSetElementHeight(element));
			if (element) resizeObserver.observe(element.firstChild);
		};

		// Helps apply the new height
		const handleSetElementHeight = (element) => {
			const height = element.firstChild.offsetHeight;
			const computedmMarginTop = parseInt(window.getComputedStyle(element).getPropertyValue('margin-top'));
			const computedmMarginBottom = parseInt(window.getComputedStyle(element).getPropertyValue('margin-bottom'));

			element.style.height = `${height + computedmMarginTop + computedmMarginBottom}px`;
		};

		// Helps hide OTP if first dfe-section collides with it
		const handleHideOTP = () => {
			// We only care for wide layouts if screen size is > 992
			if (window.innerWidth < 992) return;

			setTimeout(() => {
				const otp = document.querySelector('.on-this-page');
				const firstSection = document.querySelector('.cdc-dfe-body__center > .dfe-section');
				const blocks = firstSection?.querySelectorAll('.dfe-block--width-wide, .dfe-block--width-full_width');

				// Check if we have blocks
				if (otp && blocks && blocks.length) {
					const otpTop = window.scrollY + otp.getBoundingClientRect().top;
					const otpBottom = otpTop + otp.scrollHeight;
					const firstBlock = blocks[0];
					const firstBlockTop = window.scrollY + firstBlock.getBoundingClientRect().top;

					if (firstBlockTop < otpBottom) {
						otp.setAttribute('tabindex', '-1');
						otp.style.opacity = '0';
						otp.style.pointerEvents = 'none';
					} else {
						otp.removeAttribute('tabindex');
						otp.style.opacity = '1';
						otp.style.pointerEvents = 'auto';
					}
				}
			}, 0);
		};

		// Functionality to unstick and hide RP if under a wide/fullWidth block
		const handleUnstickAndHideRP = () => {
			// We only care for wide layouts if screen size is > 992
			if (window.innerWidth < 992) return;

			setTimeout(() => {
				const rp = document.querySelector('.page-right-rail__dynamic .related-pages');
				const blocks = document.querySelectorAll('.dfe-block--width-wide, .dfe-block--width-full_width');

				// Check if we have blocks
				if (rp && blocks.length) {
					rp.classList.add('non-sticky');

					let rpTop = window.scrollY + rp.getBoundingClientRect().top;
					const rpComputedMarginTop = parseInt(window.getComputedStyle(rp).getPropertyValue('margin-top'));
					rpTop = rpTop - (rpComputedMarginTop / 2); // subtract marginTop/2
					const lastBlock = blocks[blocks.length - 1];
					const lastBlockTop = window.scrollY + lastBlock.getBoundingClientRect().top;
					const lastBlockBottom = lastBlockTop + lastBlock.scrollHeight;

					if (rpTop < lastBlockBottom) {
						rp.setAttribute('tabindex', '-1');
						rp.style.pointerEvents = 'none';
						rp.style.opacity = '0';
					} else {
						rp.removeAttribute('tabindex');
						rp.style.pointerEvents = 'auto';
						rp.style.opacity = '1';
					}
				}
			}, 0);
		};

		// Checks if the wide block is the LAST child in the LAST dfe-section
		const handleWideBlockAdjustments = (block) => {
			const parents = document.querySelectorAll('.dfe-section'); // get all parents
			const parent = block.closest('.dfe-section'); // get the direct parent

			// Check if block's PARENT is in the last dfe-section ???
			if (parents.length > 0 && parents[parents.length - 1] === parent) {
				// Check if block is the last child
				if (parent.lastElementChild === block) {
					parent.classList.add('last-child-is-wide-block');
					block.closest('.cdc-page-content').classList.add('last-section-has-last-child-wide-block');
				}

				// Check if parent has a wide section
				// parent.classList.add('has-wide-block');
				// block.closest('.cdc-page-content').classList.add('last-section-has-wide-block');
			} else {
				return;
			}
		};

		// Loop through the 3 layouts, we only care about `wide` and `full_width`
		layouts.forEach((layout) => {
			if (layout == 'wide' || layout == 'full_width') {
				const blocks = document.body.querySelectorAll(`.dfe-block--width-${layout}`);

				if (blocks && blocks.length) {
					blocks.forEach((block) => {
						// Is the wide block a child of the "LAST" dfe-section
						handleWideBlockAdjustments(block);

						handleObserveElement(block);
					});
				}
			}
		});

		// Helps observe content area when it is resized
		// If height changed, we want to show/hide OTP and RP if needed
		const handleContentHeightChange = () => {
			// We only care for wide layouts if screen size is > 992
			if (window.innerWidth < 992) return;

			const otpResizeObserver = new ResizeObserver(() => {
				handleHideOTP();
				handleUnstickAndHideRP();
			});

			otpResizeObserver.observe(pageContent);
		};
		handleContentHeightChange();
	};

	ytPrintLinkHandler() {
		// Grab all video embeds
		const allVideos = document.querySelectorAll('.cdc-youtube-embed');

		// Only run if we have video embeds
		if (!allVideos || !allVideos.length) return;

		allVideos.forEach((video) => {
			if (!video.querySelector('iframe')) return;

			const id = video.dataset.ytId;
			const fetchData = fetch(`https://noembed.com/embed?url=https://www.youtube.com/watch?v=${id}`);

			fetchData
				.then((response) => {
					if (response.status == 'OK' || response.status == 200) return response.json();
				}).then((data) => {
					const title = data.title ? data.title : null;
					const url = data.url ? data.url : null;
					const text = document.createElement('p');
					const link = document.createElement('a');

					text.classList.add('cdc-youtube-embed--print');
					link.href = url;
					link.innerText = title;
					text.appendChild(link);
					video.appendChild(text);
				});
		});
	};

	// render beacon on attempt to print page
	printLink() {

		//eslint-disable-next-line
		if ( !window.hasOwnProperty('s') ) {
			return;
		}
		//eslint-disable-next-line
		var account = '';
		if ( window.s.hasOwnProperty( 'account' ) ) {
			account = s.account;
		} else {
			account = 'devcdc';
		}
		var imageBeaconUrl = 'https://www.cdc.gov/wcms/s.gif?action=print' +
			'&rs=' + account +
			'&url=' + encodeURIComponent( window.location.href.split( '#' )[ 0 ].split( '?' )[ 0 ] ) +
			'&pageName=' + encodeURIComponent( document.title ) +
			'&_=' + ( new Date() ).getTime().toString();

		var rule = `body:first-of-type{background-image:url(${imageBeaconUrl})}`;
		var head = document.head || document.getElementsByTagName( 'head' )[ 0 ];
		var css  = document.createElement( 'style' );

		if ( css && head ) {
			css.setAttribute( 'type', 'text/css' );
			css.setAttribute( 'media', 'print' );

			if ( css.styleSheet ) { // For IE
				css.styleSheet.cssText = rule;
			} else {
				css.appendChild( document.createTextNode( rule ) );
			}
			head.appendChild( css );
		}

	};

	tableScrollHandler() {
		const textBoxes = document.querySelectorAll('.cdc-textblock');

		textBoxes?.forEach((box) => {
			if (box) {
				const table = box.querySelector('table');

				if (table) {
					const parent = table.parentNode;
					const wrapper = document.createElement('div');

					wrapper.style.overflowX = 'auto';
					parent.insertBefore( wrapper, table );
					wrapper.appendChild( table );
				}
			}
		});
	};
}

/**
 * Simple string translation for boilerplate text for javascript
 * This is different from Wordpress's translate function but the
 * use is similar: CDC_Lang.__('Expand All');
 */
class CDC_Lang {

	static LANGS = {
		en: { name: 'English (US)', label: 'English (US)' },
		haw: { name: 'Hawaiian', label: 'ʻŌlelo Hawaiʻi' },
		es: {
			name: 'Spanish',
			label: 'Español',
			mpt: 'https://espanol.cdc.gov/enes',
		},
		zh: { name: 'Chinese', label: '中文' },
		'zh-hans': { name: 'Simplified Chinese', label: '简体中文' },
		'zh-hant': { name: 'Traditional Chinese', label: '繁體中文' },
		vi: {
			name: 'Vietnamese',
			label: 'Tiếng Việt',
			mpt: 'https://vietnamese.cdc.gov',
		},
		ko: { name: 'Korean', label: '한국어' },
		tl: { name: 'Tagalog' },
		ru: { name: 'Russian', label: 'Русский' },
		ar: { name: 'Arabic', label: 'العربية' },
		ht: { name: 'Creole', label: 'Kreyòl' },
		'es-pr': { name: 'Spanish (Puerto Rico)', label: 'Español (Puerto Rico)' },
		fr: { name: 'French', label: 'Français' },
		pl: { name: 'Polish', label: 'Polski' },
		pt: {
			name: 'Portuguese',
			label: 'Português',
			mpt: 'https://portugues.cdc.gov',
		},
		'pt-br': { name: 'Brazilian Portuguese', label: 'Português (Brasil)' },
		it: { name: 'Italian', label: 'Italiano' },
		de: { name: 'German', label: 'Deutsch' },
		ja: { name: 'Japanese', label: '日本語' },
		fa: { name: 'Farsi', label: 'فارسی' },
		ms: { name: 'Malay', label: 'Bahasa Melayu' },
		hi: { name: 'Hindi', label: 'हिन्दी' },
		th: { name: 'Thai', label: 'ภาษาไทย' },
		ase: {
			name: 'American Sign Language (ASL)',
			label: 'American Sign Language (ASL)',
		},
		am: { name: 'Amharic', label: 'ኣማርኛ' },
		my: { name: 'Burmese', label: 'ဗမာစကား' },
		prs: { name: 'Dari', label: 'درى' },
		ne: { name: 'Nepali', label: 'नेपाली' },
		ps: { name: 'Pashto', label: 'پښتو' },
		so: { name: 'Somali', label: 'af Soomaali' },
		sw: { name: 'Swahili', label: 'Kiswahili' },
		ti: { name: 'Tigrinya', label: 'ትግርኛ' },
		uk: { name: 'Ukrainian', label: 'Українська' },
		kar: { name: 'Karen', label: 'Karen' },
		rw: { name: 'Kinyarwanda', label: 'Ikinyarwanda' },
		kun: { name: 'Kunama' },
		om: { name: 'Oromo', label: 'Afaan Oromo' },
		chk: { name: 'Chuukese' },
		mh: { name: 'Marshallese' },
		to: { name: 'Tongan' },
		he: { name: 'Hebrew', label: 'עִבְרִית' },
		yi: { name: 'Yiddish', label: 'ײִדיש' },
		hmn: { name: 'Hmong' },
		sr: { name: 'Serbian', label: 'српски језик' },
		ku: { name: 'Kurdish', label: 'کوردی' },
		urd: { name: 'Urdu', label: 'اُردُو' },
		dz: { name: 'Dzongkha' },
		rn: { name: 'Rundi' },
		ilo: { name: 'Ilocano' },
		bs: { name: 'Bosnian', label: 'bosanski jezik' },
		ab: { name: 'Abkhazian' },
		aa: { name: 'Afar' },
		af: { name: 'Afrikaans' },
		ak: { name: 'Akan' },
		sq: { name: 'Albanian' },
		an: { name: 'Aragonese' },
		hy: { name: 'Armenian' },
		as: { name: 'Assemese' },
		av: { name: 'Avaric' },
		ae: { name: 'Avestan' },
		ay: { name: 'Aymara' },
		az: { name: 'Azerbaijani' },
		bm: { name: 'Bambara' },
		ba: { name: 'Bashkir' },
		eu: { name: 'Basque' },
		be: { name: 'Belarusian' },
		bn: { name: 'Bengali' },
		bi: { name: 'Bislama' },
		br: { name: 'Breton' },
		bg: { name: 'Bulgarian' },
		ca: { name: 'Catalan' },
		ch: { name: 'Chamorro' },
		ce: { name: 'Cechen' },
		ny: { name: 'Chichewa' },
		cu: { name: 'Church Slavonic' },
		cv: { name: 'Chuvash' },
		kw: { name: 'Cornish' },
		co: { name: 'Corsican' },
		cr: { name: 'Cree' },
		hr: { name: 'Croatian' },
		cs: { name: 'Czech' },
		da: { name: 'Danish' },
		dv: { name: 'Divehi' },
		nl: { name: 'Dutch' },
		eo: { name: 'Esperanto' },
		et: { name: 'Estonian' },
		ee: { name: 'Ewe' },
		fo: { name: 'Faroese' },
		fj: { name: 'Fijian' },
		fi: { name: 'Finnish' },
		fy: { name: 'Western Frisian' },
		ff: { name: 'Fulah' },
		gd: { name: 'Gaelic' },
		gl: { name: 'Galician' },
		lg: { name: 'Luganda' },
		ka: { name: 'Georgian' },
		el: { name: 'Greek' },
		kl: { name: 'Kalaallisut' },
		gn: { name: 'Guarani' },
		gu: { name: 'Gujarati' },
		ha: { name: 'Hausa' },
		hz: { name: 'Herero' },
		ho: { name: 'Hiri Motu' },
		hu: { name: 'Hungarian' },
		is: { name: 'Icelandic' },
		io: { name: 'Ido' },
		ig: { name: 'Igbo' },
		id: { name: 'Indonesian' },
		ia: { name: 'Interlingua' },
		ie: { name: 'Interlingue' },
		iu: { name: 'Inukitut' },
		ik: { name: 'Inupiaq' },
		ga: { name: 'Irish' },
		jv: { name: 'Javanese' },
		kn: { name: 'Kannada' },
		quc: { name: 'K\'iche\'' },
		kr: { name: 'Kanuri' },
		ks: { name: 'Kashmiri' },
		kk: { name: 'Kazakh' },
		km: { name: 'Central Khmer' },
		ki: { name: 'Kikuyu' },
		ky: { name: 'Kirghiz' },
		kv: { name: 'Komi' },
		kg: { name: 'Kongo' },
		kj: { name: 'Kuanyama' },
		lo: { name: 'Lao' },
		la: { name: 'Latin' },
		lv: { name: 'Latvian' },
		li: { name: 'Limburgan' },
		ln: { name: 'Lingala' },
		lt: { name: 'Lithuanian' },
		lu: { name: 'Luba Katanga' },
		lb: { name: 'Luxembourgish' },
		mk: { name: 'Macedonian' },
		mg: { name: 'Malagasy' },
		ml: { name: 'Malayalam' },
		mt: { name: 'Maltese' },
		mam: { name: 'Mam' },
		gv: { name: 'Manx' },
		mi: { name: 'Maori' },
		mr: { name: 'Marathi' },
		mn: { name: 'Mongolian' },
		nah: { name: 'Nahuatl' },
		na: { name: 'Nauru' },
		nv: { name: 'Navajo' },
		nd: { name: 'North Ndebele' },
		nr: { name: 'South Nedebele' },
		ng: { name: 'Ndonga' },
		no: { name: 'Norwegian' },
		nb: { name: 'Norwegian Bokmal' },
		nn: { name: 'Norwegian Nynorsk' },
		ii: { name: 'Sichuan Yi' },
		oc: { name: 'Occitian' },
		oj: { name: 'Ojibwa' },
		or: { name: 'Oriya' },
		os: { name: 'Ossetian' },
		pi: { name: 'Pali' },
		pa: { name: 'Punjabi' },
		qu: { name: 'Quechua' },
		ro: { name: 'Romanian' },
		rm: { name: 'Romansh' },
		se: { name: 'Northern Sami' },
		sm: { name: 'Samoan' },
		sg: { name: 'Sango' },
		sa: { name: 'Sanskrit' },
		sc: { name: 'Sardinian' },
		sn: { name: 'Shona' },
		sd: { name: 'Sindhi' },
		si: { name: 'Sinhala' },
		sk: { name: 'Slovak' },
		sl: { name: 'Slovenian' },
		st: { name: 'Southern Southo' },
		su: { name: 'Sundanese' },
		ss: { name: 'Swati' },
		sv: { name: 'Swedish' },
		ty: { name: 'Tahitian' },
		tg: { name: 'Tajik' },
		ta: { name: 'Tamil' },
		tt: { name: 'Tatar' },
		te: { name: 'Telugu' },
		bo: { name: 'Tibetan' },
		ts: { name: 'Tsonga' },
		tn: { name: 'Tswana' },
		tr: { name: 'Turkish' },
		tk: { name: 'Turkmen' },
		tw: { name: 'Twi' },
		ug: { name: 'Uighur' },
		uz: { name: 'Uzbek' },
		ve: { name: 'Venda' },
		vo: { name: 'Volapuk' },
		wa: { name: 'Walloon' },
		cy: { name: 'Welsh' },
		wo: { name: 'Wolof' },
		xh: { name: 'Xhosa' },
		yo: { name: 'Yoruba' },
		za: { name: 'Zhuang' },
		zu: { name: 'Zulu' },
	};

	constructor (string) {
		return CDC_Lang(string);
	}

	// add english on left and spanish on right
	static map = {
		es: {
			'Menu': 'Menú',
			'Close': 'Cerrar',
			'All pages': 'Todas las páginas',
			'Back to Top': 'Inicio de la página',
			'Collapse All': 'Cerrar todo',
			'Expand All': 'Expandir todo',
			'Find Information': 'Buscar información',
			'For Everyone': 'Para todos',
			'Health Care Providers': 'Proveedores de atención médica',
			'Hide Text Description': 'Esconder descripción del texto',
			'Languages': 'Idiomas',
			'More Information': 'Más información',
			'of': 'de',
			'page': 'página',
			'Page': 'Página',
			'pages': 'páginas',
			'Public Health': 'Salud pública',
			'Related Pages': 'Páginas Relacionadas',
			'Show Less':  'Mostrar menos',
			'Show More':  'Mostrar más',
			'Show Text Description': 'Mostrar descripción del texto',
			'Site Index':  'Índice del sitio',
			'Skip directly to On This Page': 'Ir a En Esta Página',
			'Table of Contents': 'Índice',
			'This photo contains content that may be sensitive to some people': 'Esta foto tiene contenido que podría ser delicado para algunas personas',
			'View All': 'Ver todo',
			'View photo': 'Ver foto',
		},
	};

	/**
	 * Translate string to page language
	 * @param {string} string
	 * @returns string
	 */
	static translate( string ) {
		let translation = String(string).trim();
		let language = CDC.Page.lang;
		if ( CDC_Lang.map[language] && CDC_Lang.map[language][string] ) {
			translation = CDC_Lang.map[language][string];
		}
		return translation;
	}

	// alias for translate
	static t(string) {
		return CDC_Lang.translate(string);
	}
	// alias for translate
	static __(string) {
		return CDC_Lang.translate(string);
	}

	// get a label for a language
	static getLabel(lang) {
		let label = null;
		let langItem = CDC_Lang.LANGS[lang];
		if (langItem) {
			label = langItem.label || langItem.name;
		}
		return label;
	}
}

/**
 * Encapsulates logic for mobile navigation features
 * Mobile menu dropdown
 * Mobile page jumplinks
 *
 * window.CDC.MobileMenu
 */
class CDCMobileMenu {
	// moved below to quiet eslint
	// static SELECTOR = '.cdc-header__logo-menu-search__mobile .dropdown-toggle';
	elements = {
		mobileMenu: null,
		mobileMenus: [],
		backdrop: null,
	};
	eventsAttached = false;

	// bs5 dropdown object
	mobileMenu = null;
	mobileCurrentAccordion = null;

	constructor() {
		this.isOpen = false;
		this.elements = {
			mobileMenu: document.querySelector('.cdc-mobile-menu'),
			mobileSearch: document.querySelector('.cdc-mobile-menu-search'),
			mobileButtons: document.querySelector('.cdc-header-mobile__buttons'),
			mobileSearchToggles: document.querySelectorAll('.cdc-header-mobile__buttons a.search-link'),
			mobileMenuToggles: document.querySelectorAll('.cdc-header-mobile__title .dropdown-toggle'),
			mobileMenus: document.querySelectorAll( CDCMobileMenu.SELECTOR ),
			navbar: document.querySelector( '.cdc-mobile-navbar__links' ),
			pagingButton: document.querySelector( '.cdc-mobile-navbar__paging' ),
			mobileAccordion: document.querySelectorAll( '.cdc-mobile-audience .accordion-button'),
		}

		if (!this.elements.mobileMenu) {
			return;
		}

		// search input
		this.elements.mobileMenu.search = this.elements.mobileSearch?.querySelector('[data-search-input]');

		// checking if pagingButton is being pressed/touched
		// check if width of mobile navbar needs pagingButton
		this.hidePagingButton();

		if (this.elements.mobileMenu) {
			this.mobileMenu = new bootstrap.Dropdown(this.elements.mobileMenu, {
				display: 'static',
				autoClose: true,
			});

			this.elements.mobileMenu.addEventListener('shown.bs.dropdown', () => {
				this.isOpen = true;
			});
			this.elements.mobileMenu.addEventListener('hidden.bs.dropdown', () => {
				this.isOpen = false;
			});

			// handles mobile search toggle
			this.elements.mobileSearchToggles.forEach(button => {
				button.addEventListener('click', (e) => {
					if (this.elements.mobileButtons.classList.contains('search-active')) {
						this.elements.mobileButtons.classList.remove('search-active');
						this.elements.mobileMenu.search.setAttribute('tabindex', -1);
					} else {
						this.elements.mobileButtons.classList.add('search-active');
						this.elements.mobileMenu.search.focus();
						this.elements.mobileMenu.search.setAttribute('tabindex', 0);
					}
				})
			})

			// handles mobile menu toggle
			this.elements.mobileMenuToggles.forEach((button) => {
				button.addEventListener('click', (event) => {
					event.preventDefault();

					// this.elements.mobileMenu.toggle();
					document.body.classList.toggle( 'mobile-menu-open' );

					if (button.classList.contains('show')) {
						setTimeout(() => {
							button.innerHTML = `${CDC_Lang.__('Close')} <i class="cdc-icon-close"></i>`;
						}, 50);
					} else {
						setTimeout(() => {
							button.innerHTML = `${CDC_Lang.__('Menu')} <i class="cdc-fa-angle-down"></i>`;
						}, 50);
					}

					if (this.isOpen) {
						// button.classList.add('menu-active');
						this.elements.mobileMenu.querySelector('button[aria-expanded="true"]')?.focus();

						// 5/31/24 by Tou: Since search is its own thing now, this is no longer relavent, only need it to toggle menu now
						// if ('search' === e.currentTarget.dataset.mobileToggle && this.elements.mobileMenu.search) {
						// 	this.elements.mobileMenu.search.focus();
						// } else {
						// 	this.elements.mobileMenu.querySelector('button[aria-expanded="true"]')?.focus();
						// }
					} else {
						// See line 87
						// button.classList.remove('menu-active');
					}
				})
			})

			// expand current audience in mobile menu
			if (CDC.Page.audience) {
				let activeAccordion = document.getElementById(`mobilemenu-${CDC.Page.audience}`);
				if (activeAccordion) {
					this.mobileCurrentAccordion = new bootstrap.Collapse(activeAccordion);
					this.mobileCurrentAccordion.show();
				}
			}

			// expand related and more from cdc audience in mobile menu
			let relatedAccordion = document.getElementById(`mobilemenu-related`);
			let cdcMoreAccordion = document.getElementById(`mobilemenu-cdcmore`);

			if (cdcMoreAccordion){
				//remove more from cdc header
				cdcMoreAccordion.querySelector('.cdc-megamenu__heading').remove()
				//extract child nodes
				let ul = cdcMoreAccordion.querySelector('.cdc-megamenu__links').childNodes[1]

				//clean up attritudes
				ul.removeAttribute('class')
				ul.removeAttribute('role')

				cdcMoreAccordion.querySelector('.accordion-body').prepend(ul)
				//remove cdc-megamenu__links
				cdcMoreAccordion.querySelector('.cdc-megamenu__links').remove()
			}
			//expand both links by default
			if ( relatedAccordion && cdcMoreAccordion ) {
				this.mobileCurrentAccordion = new bootstrap.Collapse(relatedAccordion);
				this.mobileCurrentAccordion.show();

				this.mobileCurrentAccordion = new bootstrap.Collapse(cdcMoreAccordion);
				this.mobileCurrentAccordion.show();

			} else if ( cdcMoreAccordion) {
				this.mobileCurrentAccordion = new bootstrap.Collapse(cdcMoreAccordion);
				this.mobileCurrentAccordion.show();
			}

			// focus out closes menu
			// document.addEventListener('focusin', (e) => {
			// 	if (this.isOpen && !this.elements.mobileMenu.contains(e.target) && !this.elements.mobileButtons?.contains(e.target)) {
			// 		this.mobileMenu.hide();
			// 	}
			// })

		}

		// mobile paging button
		if (this.elements.pagingButton) {
			this.elements.pagingButton.onclick = () => {
				// NOTE: nicer animation than above, but doesn't reliably scroll 300...
				this.elements.navbar.scrollBy({
					left: 100,
					behavior: 'smooth'
				});
			};
		}

		// Prevent Dropdown from being closed when clicking in accordion
		if (this.elements.mobileAccordion?.length) {
			this.elements.mobileAccordion.forEach( function(header){
				header.addEventListener( 'click', function(e){
					e.preventDefault();
					e.stopPropagation();
				});
				header.hasEventListener = true;
			});
		}
		window.addEventListener( 'resize', () => {
			this.hidePagingButton();
		});
	}

	hidePagingButton() {
		let linkwidths = 0;
		const links = document.querySelectorAll( '.cdc-mobile-navbar-links a' );
		if (links?.length) {
			links.forEach( ( item ) => {
				linkwidths += item.offsetWidth + 18; // adding up links and gap widths
			} );
			if ( linkwidths <= this.elements.navbar.offsetWidth ) {
				this.elements.pagingButton.style.display = 'none';
			} else {
				this.elements.pagingButton.style.display = 'block';
			}
		}
	}
}

CDCMobileMenu.SELECTOR = '.cdc-header__logo-menu-search__mobile .dropdown-toggle';
class USWDSBanner {
	constructor() {
		this.banner = document.querySelector('.cdc-site-gov-notice');
		this.bannerBtn = document.querySelector('a[data-bs-toggle="collapse"');
		this.bannerBody = document.querySelector('#gov-notice');

		CDC.Page.on('init', () => this.init());
	}

	init() {
		// addinga fail-safe, if no uswds banner then do nothing
		// homepages don't have mega menus
		if (!this.banner) return;

		this.bannerBtn.addEventListener('click', (event) => {
			if (event.target.classList.contains('collapsed')) {
				this.bannerBody.setAttribute('aria-hidden', true);
			} else {
				this.bannerBody.setAttribute('aria-hidden', false);
			}
		});
	}
}

class CDCTopMenu {
	constructor() {
		CDC.Page.on('init', () => this.init());
	}

	init() {
		// NOTE TO FUTURE JS DEV
		// below needs to be added to above - thanks!

		const headerBody = document.querySelector('.cdc-header__body');

		if ( null === headerBody ) {
			return;
		}

		const headerMenu = headerBody.querySelector('.cdc-header__menu');
		const headerLinks = headerBody.querySelector('.cdc-header__links');

		if (!headerMenu) {
			// check if we have headerLinks
			if (!headerLinks) headerBody.classList.add('align-to-bottom');
		}

		// the cdc-megamenu container
		const megaMenu = document.querySelector('.cdc-megamenu');

		// homepages don't have mega menus
		if (!megaMenu) {
			return;
		}

		// observes whenever the 'cdc-megamenu-open' class is added/removed from the body tag
		let prevClassState = document.body.classList.contains('cdc-megamenu-open');
		const classObserver = new MutationObserver((mutations) => {
			mutations.forEach((mutation) => {
				if ('class' === mutation.attributeName){
					var currentClassState = mutation.target.classList.contains('cdc-megamenu-open');
					if (prevClassState !== currentClassState)    {
						prevClassState = currentClassState;
						if (currentClassState) {
							handleMegaMenuNavFocus(true);
						} else {
							handleMegaMenuNavFocus(false);
						}
					}
				}
			});
		});
		classObserver.observe(document.body, { attributes: true });

		const megaButton = headerBody.querySelector('#megaButton');

		// clicking on the button should open the menu. It should also not propagate up because it'll trigger window.onclick
		// opening or closing the menu is done by toggling the cdc-megamenu-open class on the body
		megaButton?.addEventListener( 'click', function( e ) {
			$(e.target).trigger( 'dfe_custom_interaction' );
			e.stopImmediatePropagation();
			document.body.classList.toggle( 'cdc-megamenu-open' );
		} );

		// when clicking anywhere in the window, if the menu is open and they've clicked outside of the menu toggle it closed
		window.addEventListener('click', function( e ) {
			const menuIsOpen = document.body.classList.contains( 'cdc-megamenu-open' );

			// if(document.querySelector('.cdc-megamenu').contains(e.target)) {
			// 	document.body.classList.toggle( 'cdc-megamenu-open' );
			// }
			if ( menuIsOpen && null === e.target.closest( '.cdc-megamenu' ) ) {
				document.body.classList.toggle( 'cdc-megamenu-open' );
			}
		});

		// grab all the focusable items in the megaMenu
		const focusableItems = megaMenu.querySelectorAll('a, button');

		// fn to help set tabindex for all focusableItems in megaMenu
		const handleMegaMenuNavFocus = (activate) => {
			for (let i = 0; i < focusableItems.length; i++) {
				focusableItems[i].setAttribute('tabindex', !activate ? '-1' : '0');
			}
		};
		// Run it!
		handleMegaMenuNavFocus();

		// helps trap focus in the megamenu nav since it is treated as a modal
		// detect when focusing out...
		document.addEventListener('focusout', (event) => {
			// if our megamenu is active/open
			if (document.body.classList.contains( 'cdc-megamenu-open' )) {
				// if the last focused item is the last focusable item in megaMenu
				if (event.target === focusableItems[focusableItems.length - 1]) {
					// focus on the megaButton
					megaButton.focus();
				}
			}
		});
	}
}

class CDCBottomMenu {
	constructor() {
		this.footer = document.querySelector('.cdc-footer');
		if (!this.footer) {
			return;
		}
		this.innerFooter = this.footer.querySelector('.cdc-footer__inner');
		this.links = this.innerFooter.querySelectorAll('[data-bs-toggle="collapse"');
		this.subnavs = this.innerFooter.querySelectorAll('.cdc-footer__subnav');

		CDC.Page.on('init', () => this.init());
	}

	init() {
		this.links.forEach((element) => {
			const subnav = document.querySelector(`${element.getAttribute('href')}`);

			// Subnavs are hidden visually through CSS
			// But they are still available DOM-wise because we want to grab the computed div height
			// Though we are hidden visually, the below will stop screen readers from access the subnav
			// As well as user's being able to tab into it
			subnav.setAttribute('aria-hidden', true);
			subnav.setAttribute('data-height', subnav.clientHeight);

			// When users click on a footer link
			element.addEventListener('click', (event) => {
				// Because we don't control the adding/removing of the 'show' class...
				// We create a mutationObserver to check when the subnav gets the 'show' class
				let prevClassState = subnav.classList.contains('show');
				const classObserver = new MutationObserver((mutations) => {
					mutations.forEach((mutation) => {
						if ('class' === mutation.attributeName){
							const currentClassState = mutation.target.classList.contains('show');

							if (prevClassState !== currentClassState)    {
								prevClassState = currentClassState;

								if (currentClassState) {
									// Give the innerFooter padding so our abolustely positioned subnav can show naturally...
									this.innerFooter.style.paddingBottom = `${subnav.getAttribute('data-height')}px`;
								} else {
									this.innerFooter.style.paddingBottom = `${0}px`;
								}
							}
						}
					});
				});
				classObserver.observe(subnav, { attributes: true });
			});
		});
	}
}

/**
 * Handles loading necessary CSS / JS assets for individual page modules
 */
class CDCModules {

	static loaded = {};

	// in prod we use minified files
	static minSuffix = CDC.Common.isProd ? '.min' : '';

	/**
	 * This is the full list of modules supported
	 *
	 *   selector:  {string}       is the DOM selector to test presence of modules on the page
	 *   js:        {string|array} relative path(s) to any JS files to load, in order
	 *   css:       {string|array} relative path(s) to any CSS files to load, in order
	 *
	 */
	static MODULES = {
		datatable: {
			selector: '.cdc-datatable-module',
			js: `/TemplatePackage/5.0/js/modules/datatable${CDCModules.minSuffix}.js`,
		},
		sortfilter: {
			selector: 'sort-filter-root',
			js: [ '/TemplatePackage/5.0/js/modules/sortfilter.js', '/TemplatePackage/contrib/apps/sortfilter.js' ],
			css: '/TemplatePackage/5.0/css/modules/sortfilter.min.css'
		},
		jumplinks: {
			selector: '.dfe-callout--jump-link',
			js: `/TemplatePackage/5.0/js/modules/jump-links${CDCModules.minSuffix}.js`,
		},
		contentcollection: {
			selector: 'content-collection',
			js: '/TemplatePackage/contrib/apps/contentcollection/widget.js',
		},
		orgChartAccordion: {
			selector: '[data-app="orgChart"][data-type="accordion"]',
			js: '/TemplatePackage/contrib/apps/orgchart/react-accordions.js',
		},
		orgChartInteractive: {
			selector: '[data-app="orgChart"][data-type="interactive"]',
			js: '/TemplatePackage/contrib/apps/orgchart/react-orgcharts.js',
		},
	};

	static load() {
		Object.entries(CDCModules.MODULES).forEach(([module, config]) => {
			if (!CDCModules.loaded[module] && $(config.selector).length) {

				// load module assets
				if (config.js) {
					const jsFiles = CDC.Common.toArray(config.js)
						.filter((file) => !!String(file||'').trim())
						.map(file => CDC.tpPath + file);

					CDC.Common.loadJS(jsFiles, () => CDCModules.ready(module, config));
				}
				if (config.css) {
					const cssFiles = CDC.Common.toArray(config.css)
						.filter((file) => !!String(file||'').trim())
						.map(file => CDC.tpPath + file);

					CDC.Common.loadCSS(cssFiles);
				}
			}
		});
	}

	static ready(module, config) {
		console.info(`Module ${module} ready`);
		CDCModules.loaded[module] = true;
	}

}

/**
 * Handles loading necessary CSS / JS assets for individual page modules
 */
class CDCNavigation {
	nav = {};
	flatNav = [];
	site = {};
	nodes = {};
	homepage = {};
	toc = {};
	audienceNames = {
		gen : CDC_Lang.__('For Everyone'),
		hcp : CDC_Lang.__('Health Care Providers'),
		php : CDC_Lang.__('Public Health')
	}

	// current url, "normalized" for comparison
	currentNormalizedUrl = CDC.Common.normalizeUrl(location.href);

	navCurrent = null;
	navCurrentIndex = 0;
	navNext = null;

	constructor() {
		this.init();
	}

	init() {
		if (CDC.Page.syndicated) {
			console.debug('CDCNavigation: syndicated content, skip navigation.');
			return;
		}
		// exit if CDC homepage
		if ('cdc_homepage' === CDC.Page.type) {
			return;
		}
		this.nodes = {
			related: document.querySelector('[data-related-nav]'),
			related_mobile: document.querySelector('[data-related-nav-mobile]'),
			journey: document.querySelector('[data-journey-next]'),
		};
		this.load()
			.then(() => this.render())
			//.catch((e) => console.error('Failed loading nav:', e));

		this.addSkipToOTP();
	}

	load() {
		return new Promise((resolve, reject) => {
			// when previewing nav is available locally
			if ('object' === typeof window.CDC_SITE_NAV) {
				this.processNav(Object.assign({}, window.CDC_SITE_NAV));
				return resolve();
			}

			// don't load locally
			if ('localhost' === window.location.hostname) {
				return resolve()
			}

			if (!CDC.Page.config.nav || !CDC.Page.context) {
				return resolve();
			}

			// test
			let navUrl = CDC.Page.config.nav + (CDC.Page.isSpanish ? '/es' : '') + `/nav.${CDC.Page.context}.json`;

			$.ajax({
				url: navUrl,
				method: 'get',
				contentType: 'json',
			})
				.then((nav) => {
					this.processNav(Object.assign({}, nav));
					return resolve();
				})
				.catch((e) => {
					//console.error('Failed to load nav:', e);
					return reject(e);
				});
		});
	}

	// looks through nav for some details relative to current page
	processNav(nav) {
		this.nav = nav;
		this.site = Object.assign(this.site, nav.site);
		if (this.site.homepage) {
			this.homepage = this.site.homepage;
		}

		// build flat nav for sequential crawling
		// eslint-disable-next-line no-undef
		CDCPage.AUDIENCES.forEach((audience) => {
			if (!this.nav[audience]?.length) {
				return;
			}
			this.flatNav = this.flatNav.concat(this.getFlatNavs(this.nav[audience], audience));
			this.nav[audience] = nav[audience];
		});

		// if we don't have a next nav item, it's the first nav item
		if (!this.navNext && this.flatNav.length && this.isCurrentNav(this.flatNav[0])) {
			this.navNext = this.flatNav[0];
		}
		CDC.Page.emit('navLoaded', this.nav);
	}

	addSkipToOTP() {
		// Find the first element with the .on-this-page class
		const OTP = document.querySelector( '.on-this-page' );
		const skipmenu = document.getElementById( 'skipmenu' );

		if ( OTP && skipmenu ) {
			// Add an ID to the element
			OTP.id = 'first-on-this-page';

			// Create a new skipmenu link
			const skiplink = document.createElement( 'a' );
			skiplink.href = `#first-on-this-page`;
			skiplink.textContent = CDC_Lang.__('Skip directly to On This Page');
			skiplink.classList.add( 'visually-hidden-focusable' );

			// Append the skiplink
			skipmenu.appendChild( skiplink );
		}
	}

	// If we have a site alert, render it
	processSiteAlert() {
		const alertEnabled = this.site?.alert?.enabled || false;
		if (!alertEnabled) {
			return;
		}

		const title = this.site?.alert?.title || false;
		const body = this.site?.alert?.body || false;
		const type = this.site?.alert?.type || false;
		const link = this.site?.alert?.link || false;
		const linkText = this.site?.alert?.link_text || false;

		//Exists on most pages, insert site alert right after this element.
		const siteAlert = document.querySelector('[data-cdc-site-alert]');

		//Site Alert required a type, title, and body. Also, the page header must exist
		if (!type || !siteAlert) {
			return;
		}

		if (!title && !body) {
			return;
		}

		let linkButtonHtml = linkText && link ? `<a class="alert-action-link" href="${CDC.cleanAttr(link)}">${linkText}</a>` : '';
		let titleHtml = String(title || '').trim() ? `<div class="alert-heading">${title}</title></div>` : '';
		let bodyHtml = String(body || '').trim() ? `<p class="alert-body">${body}</p>` : '';
		let alertClass = 'alert-info';
		if ('success' === type) {
			alertClass = 'alert-success';
		}
		if ('danger' === type) {
			alertClass = 'alert-danger';
		}
		if ('warning' === type) {
			alertClass = 'alert-warning';
		}
		if ('notification' === type) {
			alertClass = 'alert-notification';
		}
		$(siteAlert).prepend(`
			<div class="site-alert alert ${alertClass}" role="status" aria-live="polite">
				<div class="site-alert__wrapper">
					<i class="site-alert__icon alert-icon"></i>
					<div class="site-alert__body">
						${titleHtml}
						${bodyHtml}
						${linkButtonHtml}
					</div>
				</div>
			</div>
		`);
	}

	/**
	 * Flattens the nav to 1 list
	 * @param {array} navs array of nav items
	 * @param {string} audience Audience of nav
	 * @param {int} level Level of nav items, default 1
	 * @returns {array}
	 */
	getFlatNavs(navs, audience, parent, level) {
		level = level || 1;
		let flatNavs = [];
		if (!Array.isArray(navs)) {
			return flatNavs;
		}
		navs.forEach((nav) => {
			nav.audience = audience;
			nav.level = level;
			if (parent) {
				nav.parent = parent;
			}

			// catch the current nav item and next item
			if (!this.navCurrent && nav?.url && this.isCurrentNav(nav)) {
				this.navCurrent = nav;
				nav.active = true;
			}
			if (this.navCurrent && !this.navNext) {
				// If A Child, Next Logical Link is a Sibling
				if (this.navCurrent.parent) {
					let siblings = this.navCurrent.parent.children;
					let parentIndex = this.nav[audience].findIndex(
						(sibling) => sibling.post_id === this.navCurrent.parent.post_id
					);
					let currentIndex = siblings.findIndex((child) => child.post_id === this.navCurrent.post_id);

					// If We Have No Siblings to Point To
					if (parentIndex !== this.nav[audience].length - 1) {
						// Point to Next Parent if No More Siblings
						if (currentIndex === siblings.length - 1) {
							this.navNext = this.nav[audience][parentIndex + 1];
							// Point to Next Sibling if not Last Child
						} else if (currentIndex !== siblings.length - 1) {
							this.navNext = siblings[currentIndex + 1];
						}
						// If Our Parent is Last Parent, Start at Beginning of our Audience
					} else if (parentIndex === this.nav[audience].length - 1) {
						// Point to First Parent if No More Siblings
						if (currentIndex === siblings.length - 1) {
							// HomePage can't be the Next Item, so get 2nd
							if (this.nav[audience][0].homepage) {
								this.navNext = this.nav[audience][1];
							} else {
								this.navNext = this.nav[audience][0];
							}
							// Point to Sibling if not Last Child
						} else if (currentIndex !== siblings.length - 1) {
							this.navNext = siblings[currentIndex + 1];
						}
					}
				} else {
					let parentIndex = this.nav[audience].findIndex(
						(sibling) => sibling.post_id === this.navCurrent.post_id
					);
					// If We Are a Parent, Point to First Child
					if (this.navCurrent.children && 0 < this.navCurrent.children.length) {
						this.navNext = this.navCurrent.children[0];
						// If No Children, Point to Next Parent
					} else if (!this.navCurrent.children || 0 === this.navCurrent.children.length) {
						if (parentIndex !== this.nav[audience].length - 1) {
							this.navNext = this.nav[audience][parentIndex + 1];
							// If Last Parent, Point to Beginning of Audience.
						} else {
							if (this.nav[audience][0].homepage) {
								this.navNext = this.nav[audience][1];
							} else {
								this.navNext = this.nav[audience][0];
							}
						}
					}
				}
			}

			flatNavs.push(nav);
			if (nav.children?.length) {
				flatNavs = flatNavs.concat(this.getFlatNavs(nav.children, audience, nav, level + 1));
			}
		});
		return flatNavs;
	}

	// test on each nav element if it represents current page
	isCurrentNav(nav) {
		let postId = CDC.Page.postId;
		if (this.testPostId) {
			postId = this.testPostId;
		}
		let isCurrentNav = false;

		if (postId) {
			isCurrentNav = postId === nav.post_id;
		} else {
			isCurrentNav = CDC.Common.normalizeUrl(nav?.url) === this.currentNormalizedUrl;
		}

		// outside case page isn't English or Spanish, test alt langs
		if (!CDC.Page.isEnglish && !CDC.Page.isSpanish && Array.isArray(nav.alt_langs)) {
			let altLangMatch = nav.alt_langs.find(item => item?.post_id === postId);
			isCurrentNav = isCurrentNav || !!altLangMatch;
		}
		return isCurrentNav;
	}

	/**
	 * Test nav elements with a given postId
	 * @param {int} postId
	 */
	testNav(postId) {
		this.navCurrent = null;
		this.navNext = null;
		this.testPostId = parseInt(postId);
		this.load()
			.then(() => {
				// when testing, page assumes audience of current nav
				CDC.Page.audience = this.navCurrent?.audience;
				this.render();
			})
			//.catch((e) => console.error('Failed loading nav:', e));
	}

	render() {
		if (!this.nav) {
			return;
		}
		if (this.nodes.related) {
			this.renderRelated();
		}
		if (this.nodes.journey) {
			this.renderJourney();
		}
		this.renderLangLinks();
		this.renderBreadcrumb();

		this.processSiteAlert();

		// possibly render table of contents
		this.renderTOC();

		this.toggleAudiences();
	}

	fillL1sAbove(originalArray, startingIndex, resultArray, count, currentIndex, remainingSpots) {
		let spotsLeft = 0;
		let itemsAbove = Math.min(count, startingIndex);
		for (let i = 1; i <= itemsAbove && 0 < remainingSpots; i++) {
			const currentIndexAbove = (startingIndex - i + originalArray.length) % originalArray.length;
			if (currentIndexAbove !== currentIndex) {
				if (currentIndexAbove >= 0) {
					resultArray.unshift(originalArray[currentIndexAbove]);
					remainingSpots--;
				}
			}
		}
		spotsLeft = remainingSpots;
		return spotsLeft;
	}

	fillItemsBelow(originalArray, startingIndex, resultArray, count, currentIndex, remainingSpots) {
		let spotsLeft = 0;
		let currentIndexBelow = (startingIndex + 1) % originalArray.length;
		const itemsBelow = Math.min(count, originalArray.length - startingIndex - 1);
		for (let i = 0; i < itemsBelow && 0 < remainingSpots; i++) {
			if (currentIndexBelow !== currentIndex && currentIndexBelow < originalArray.length) {
				resultArray.push(originalArray[currentIndexBelow]);
				remainingSpots--;
			}
			currentIndexBelow = (currentIndexBelow + 1) % originalArray.length;
		}
		spotsLeft = remainingSpots;
		return spotsLeft;
	}

	renderRelated() {
		if (!this.nodes.related || !this.navCurrent) {
			return;
		}

		let nextNavs = [];
		let linksToShow = 5;
		let currentAudience = CDC.Page.audience;
		if (!Array.isArray(this.nav[currentAudience])) {
			return;
		}

		let audienceArray = this.nav[currentAudience].filter((nav, index) => !nav.homepage);
		let audienceHome = this.nav[currentAudience].filter((nav) => nav.homepage);
		audienceHome = audienceHome.length ? audienceHome[0] : {};
		let totalLinks = audienceArray.length;

		if (!this.nodes.related || !this.navCurrent) {
			return;
		}
		this.nodes.related.innerHTML = '';
		this.navCurrentIndex = audienceArray.findIndex((item) => item?.post_id === this.navCurrent?.post_id);

		function flattenChildren(link) {
			let flattened = [];
			if (link?.children) {
				for (const child of link.children) {
					if ( !child.exclude?.relatedPages) {
						flattened.push(child);
						const flattenedChild = flattenChildren(child);
						flattened = flattened.concat(flattenedChild);
					}
				}
			}
			return flattened;
		}

		// find next pages for related nav items
		// Make sure they are related
		// L1 Logic With/Without Children
		if (1 === this.navCurrent?.level) {
			let results = flattenChildren(audienceArray[this.navCurrentIndex]);
			// If We have Exactly 5 OR 6 Children.
			if (6 === results.length || linksToShow === results.length) {
				nextNavs.push(...results);
				// More than 5 Children of L1 Logic
			} else if (results.length > linksToShow) {
				for (let i = 0; i < linksToShow; i++) {
					nextNavs.push(results[i]);
				}
				// Less than 5 Children of L1 Logic
			} else if (results.length < linksToShow) {
				let remainingSlots = linksToShow - results.length;
				// First L1 Logic
				if (0 === this.navCurrentIndex) {
					for (let nav of audienceArray) {
						if (results.length < linksToShow) {
							if (
								nav?.url &&
								nav?.title &&
								!this.isCurrentNav(nav) &&
								!nextNavs.find((item) => item?.post_id === nav?.post_id)
							) {
								results.push(nav);
							}
						} else {
							break;
						}
					}
					nextNavs = [...results];
					// If Somewhere In Between
				} else if (
					0 !== this.navCurrentIndex &&
					this.navCurrentIndex !== totalLinks - 1 &&
					this.navCurrentIndex !== Math.floor(totalLinks / 2)
				) {
					let lastIndex = audienceArray.length - 1;
					let remainder;
					// We Only Want to Follow Position Logic if We Have no children
					if (results.length === 0) {
						// Logic to Check if Item is Among the last 5 Items
						if (this.navCurrentIndex > Math.floor(totalLinks / 2)) {
							if (this.navCurrentIndex === lastIndex - 1) {
								// If it's the 2nd to last item, grab the last item and fill with up to 4 L1s above
								// If our 2nd to last item has any children, we need to be sure we arent adding items ABOVE them
								let tempArray = [];
								tempArray.push(audienceArray[lastIndex]);
								this.fillL1sAbove(
									audienceArray,
									lastIndex - 1,
									tempArray,
									4,
									this.navCurrentIndex,
									remainingSlots - 1
								);
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else if (this.navCurrentIndex === lastIndex - 2) {
								// If it's the 3rd to last item, grab the two last items and fill with up to 3 L1s above
								let tempArray = [];
								remainder = this.fillItemsBelow(
									audienceArray,
									lastIndex - 2,
									tempArray,
									2,
									this.navCurrentIndex,
									remainingSlots
								);
								if (0 < remainder) {
									this.fillL1sAbove(
										audienceArray,
										lastIndex - 2,
										tempArray,
										3,
										this.navCurrentIndex,
										remainder
									);
								}
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else if (this.navCurrentIndex === lastIndex - 3) {
								// If it's the 4th to last item, grab the three last items and fill with up to 2 L1s above
								let tempArray = [];
								remainder = this.fillItemsBelow(
									audienceArray,
									lastIndex - 3,
									tempArray,
									3,
									this.navCurrentIndex,
									remainingSlots
								);
								if (0 < remainder) {
									this.fillL1sAbove(
										audienceArray,
										lastIndex - 3,
										tempArray,
										2,
										this.navCurrentIndex,
										remainder
									);
								}
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else if (this.navCurrentIndex === lastIndex - 4) {
								// If it's the 5th to last item
								// If there are at least 2 above, grab the 2 above and the 3 below
								let tempArray = [];
								if (audienceArray.length >= 2) {
									remainder = this.fillL1sAbove(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										2,
										this.navCurrentIndex,
										remainingSlots
									);
									if (0 < remainder) {
										this.fillItemsBelow(
											audienceArray,
											this.navCurrentIndex,
											tempArray,
											3,
											this.navCurrentIndex,
											remainder
										);
									}
								} else {
									remainder = this.fillL1sAbove(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										1,
										this.navCurrentIndex,
										remainingSlots
									);
									if (0 < remainder) {
										this.fillItemsBelow(
											audienceArray,
											this.navCurrentIndex,
											tempArray,
											4,
											this.navCurrentIndex,
											remainder
										);
									}
								}
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else {
								let startingIndex = this.navCurrentIndex;
								let itemsBefore = 2;
								let itemsAfter = 3;
								// Calculate the actual range based on the available items
								let startIndexBefore = Math.max(0, startingIndex - itemsBefore);
								let endIndexBefore = startingIndex - 1;
								let startIndexAfter = startingIndex + 1;
								let endIndexAfter = startingIndex + itemsAfter;

								// Grab items from the non-empty array based on the calculated ranges
								let itemsToAdd = audienceArray
									.slice(startIndexBefore, endIndexBefore + 1)
									.concat(audienceArray.slice(startIndexAfter, endIndexAfter + 1));

								results = results.concat(itemsToAdd.slice(0, remainingSlots));
							}
						} else if (this.navCurrentIndex < Math.floor(totalLinks / 2)) {
							if (this.navCurrentIndex === 1) {
								let tempArray = [];
								remainder = this.fillL1sAbove(
									audienceArray,
									this.navCurrentIndex,
									tempArray,
									1,
									this.navCurrentIndex,
									remainingSlots
								);
								if (0 < remainder) {
									this.fillItemsBelow(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										4,
										this.navCurrentIndex,
										remainder
									);
								}
								// Trim to 5
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else if (this.navCurrentIndex === 2) {
								// If it's the 3rd item, grab the 2 previous L1 and the 3 After
								// If We Have Children, They Need to be Top
								let tempArray = [];
								remainder = this.fillL1sAbove(
									audienceArray,
									this.navCurrentIndex,
									tempArray,
									2,
									this.navCurrentIndex,
									remainingSlots
								);
								if (0 < remainder) {
									this.fillItemsBelow(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										3,
										this.navCurrentIndex,
										remainder
									);
								}
								// Trim to 5
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else if (this.navCurrentIndex === 3) {
								// If its 4th In the List
								let tempArray = [];
								if (audienceArray.length >= this.navCurrentIndex + 3) {
									// If there are at least 3 L1s below, grab the 2 above and 3 below
									remainder = this.fillL1sAbove(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										2,
										this.navCurrentIndex,
										remainingSlots
									);
									if (0 < remainder) {
										this.fillItemsBelow(
											audienceArray,
											this.navCurrentIndex,
											tempArray,
											3,
											this.navCurrentIndex,
											remainder
										);
									}
									// Else grab the 3 above and 2 below
								} else {
									remainder = this.fillL1sAbove(
										audienceArray,
										this.navCurrentIndex,
										tempArray,
										3,
										this.navCurrentIndex,
										remainingSlots
									);
									if (0 < remainder) {
										this.fillItemsBelow(
											audienceArray,
											this.navCurrentIndex,
											tempArray,
											2,
											this.navCurrentIndex,
											remainder
										);
									}
								}
								// Trim to 5
								results = results.concat(tempArray);
								results.splice(linksToShow);
							} else {
								let startingIndex = this.navCurrentIndex;
								let itemsBefore = 2;
								let itemsAfter = 3;
								// Calculate the actual range based on the available items
								let startIndexBefore = Math.max(0, startingIndex - itemsBefore);
								let endIndexBefore = startingIndex - 1;
								let startIndexAfter = startingIndex + 1;
								let endIndexAfter = startingIndex + itemsAfter;

								// Grab items from the non-empty array based on the calculated ranges
								let itemsToAdd = audienceArray
									.slice(startIndexBefore, endIndexBefore + 1)
									.concat(audienceArray.slice(startIndexAfter, endIndexAfter + 1));

								results = results.concat(itemsToAdd.slice(0, remainingSlots));
							}
						}
						// Put them All Together
						nextNavs = [...results];
					} else {
						let itemsBeforeIndex = (this.navCurrentIndex - 1 + audienceArray.length) % audienceArray.length;
						// let itemsAfter = remainingSlots - itemsBefore;
						let nav = audienceArray[itemsBeforeIndex];
						if (0 === results.length) {
							results.unshift(nav);
						} else {
							results.push(nav);
						}
						remainingSlots--;
						for (let i = 1; i <= remainingSlots; i++) {
							let currentIndex = (this.navCurrentIndex + i) % audienceArray.length;
							nav = audienceArray[currentIndex];
							if (
								nav?.url &&
								nav?.title &&
								!this.isCurrentNav(nav) &&
								!results.find((item) => item?.post_id === nav?.post_id)
							) {
								results.push(nav);
							}
						}
						// Put them All Together
						nextNavs = [...results];
					}
					// Last L1 Logic
				} else if (this.navCurrentIndex === totalLinks - 1) {
					let tempArray = [];
					for (
						let i = this.navCurrentIndex - 1;
						i >= Math.max(this.navCurrentIndex - remainingSlots, 0);
						i--
					) {
						let nav = audienceArray[i];
						// Temp Array to get the Subsequent L1s in the Right Order.
						if (
							nav?.url &&
							nav?.title &&
							!this.isCurrentNav(nav) &&
							!results.find((item) => item?.post_id === nav?.post_id)
						) {
							tempArray.unshift(nav);
						}
					}
					results = results.concat(tempArray);
					nextNavs = [...results];
					// Middle without Children Logic
				} else if (this.navCurrentIndex === Math.floor(totalLinks / 2) && 0 === results.length) {
					for (let i = this.navCurrentIndex - 2; i <= this.navCurrentIndex + 3; i++) {
						let currentIndex = (i + totalLinks) % totalLinks;
						let nav = audienceArray[currentIndex];
						if (
							nav?.url &&
							nav?.title &&
							!this.isCurrentNav(nav) &&
							!results.find((item) => item?.post_id === nav?.post_id)
						) {
							results.push(nav);
						}
					}
					nextNavs = [...results];
					// Middle with Children Logic
					// Always Grab the L1 Before and the Remaining Slots go to Subsequent L1s
				} else if (this.navCurrentIndex === Math.floor(totalLinks / 2) && 0 !== results.length) {
					for (let i = this.navCurrentIndex - 1; i <= this.navCurrentIndex + (remainingSlots - 1); i++) {
						let currentIndex = (i + totalLinks) % totalLinks;
						let nav = audienceArray[currentIndex];
						if (
							nav?.url &&
							nav?.title &&
							!this.isCurrentNav(nav) &&
							!results.find((item) => item?.post_id === nav?.post_id)
						) {
							results.push(nav);
						}
					}
					nextNavs = [...results];
				}
			}
		} else if (2 === this.navCurrent?.level) {
			// #L2 Logic
			// If We're Starting on L2 Level, Find our Parent L1 and Sibling L2s
			if (this.navCurrent.parent) {
				let siblings = flattenChildren(this.navCurrent.parent);
				let parentIndex = audienceArray.findIndex((item) => item.title === this.navCurrent.parent.title);
				//  #1 5 Sibling Logic
				if (siblings.length - 1 === linksToShow) {
					siblings = siblings.filter((item) => item.title !== this.navCurrent.title);
					nextNavs = [audienceArray[parentIndex], ...siblings];
					// #2  Less than 5 Sibling Logic
				} else if (siblings.length - 1 < linksToShow) {
					for (let i = 0; i <= siblings.length; i++) {
						let nav = siblings[i];
						if (
							nav?.url &&
							nav.title &&
							!this.isCurrentNav(nav) &&
							!nextNavs.find((item) => item?.post_id === nav?.post_id)
						) {
							nextNavs.push(nav);
						}
					}
					// Add Parent to Top:
					nextNavs.unshift(audienceArray[parentIndex]);
					// If We Have Spots Left Over, Grab the L1 Before the Parent too as long as our parent is the 1st parent
					if (nextNavs.length < linksToShow) {
						if (0 !== parentIndex) {
							nextNavs.push(audienceArray[parentIndex - 1]);
						}
					}
					// #3 More than 5 Sibling Logic
				} else if (siblings.length - 1 > linksToShow) {
					let remainingSlots = linksToShow;
					let remainder;
					let lastIndex = siblings.length - 1;
					// If In First Half of Siblings Logic
					let childIndex = siblings.findIndex((child) => child.title === this.navCurrent.title);
					// If First Child
					if (childIndex === 0) {
						for (let child of siblings) {
							if (nextNavs.length < linksToShow) {
								if (
									child?.url &&
									child?.title &&
									!this.isCurrentNav(child) &&
									!nextNavs.find((item) => item?.post_id === child?.post_id)
								) {
									nextNavs.push(child);
								}
							} else {
								break;
							}
						}
						nextNavs = [...nextNavs];
					}
					// If Second Child
					if (childIndex === 1) {
						let tempArray = [];
						remainder = this.fillL1sAbove(siblings, childIndex, tempArray, 1, childIndex, remainingSlots);
						if (0 < remainder) {
							this.fillItemsBelow(siblings, childIndex, tempArray, 4, childIndex, remainder);
						}
						// Trim to 5
						nextNavs = nextNavs.concat(tempArray);
						nextNavs.splice(linksToShow);
					}
					// If Middle Sibling Logic
					if (childIndex === Math.floor(siblings.length / 2)) {
						for (let i = childIndex - 2; i <= childIndex + 2; i++) {
							let currentIndex = (i + siblings.length) % siblings.length;
							let nav = siblings[currentIndex];
							if (
								nav?.url &&
								nav?.title &&
								!this.isCurrentNav(nav) &&
								!nextNavs.find((item) => item?.post_id === nav?.post_id)
							) {
								nextNavs.push(nav);
							}
						}
						nextNavs = [...nextNavs];
					}
					// If 3rd to Last
					if (childIndex === lastIndex - 2) {
						let tempArray = [];
						remainder = this.fillItemsBelow(
							siblings,
							lastIndex - 2,
							tempArray,
							2,
							childIndex,
							remainingSlots
						);
						if (0 < remainder) {
							this.fillL1sAbove(siblings, lastIndex - 2, tempArray, 3, childIndex, remainder);
						}
						nextNavs = nextNavs.concat(tempArray);
						nextNavs.splice(linksToShow);
					}
					// If 2nd to Last
					if (childIndex === lastIndex - 1) {
						let tempArray = [];
						tempArray.push(siblings[lastIndex]);
						this.fillL1sAbove(siblings, lastIndex - 1, tempArray, 4, childIndex, remainingSlots - 1);
						nextNavs = nextNavs.concat(tempArray);
						nextNavs.splice(linksToShow);
					}
					// If Last Child
					if (childIndex === lastIndex) {
						let tempArray = [];
						for (let i = childIndex - 1; i >= Math.max(childIndex - remainingSlots, 0); i--) {
							let nav = siblings[i];
							// Temp Array to get the Subsequent L1s in the Right Order.
							if (
								nav?.url &&
								nav?.title &&
								!this.isCurrentNav(nav) &&
								!nextNavs.find((item) => item?.post_id === nav?.post_id)
							) {
								tempArray.unshift(nav);
							}
						}
						nextNavs = nextNavs.concat(tempArray);
						nextNavs = [...nextNavs];
					}
					// If Somewhere In Between
					if (
						0 !== childIndex &&
						childIndex !== siblings - 1 &&
						childIndex !== Math.floor(siblings.length / 2)
					) {
						let itemsBefore = 2;
						let itemsAfter = 2;
						// Calculate the actual range based on the available items
						let startIndexBefore = Math.max(0, childIndex - itemsBefore);
						let endIndexBefore = childIndex - 1;
						let startIndexAfter = childIndex + 1;
						let endIndexAfter = childIndex + itemsAfter;

						// Grab items from the non-empty array based on the calculated ranges
						let itemsToAdd = siblings
							.slice(startIndexBefore, endIndexBefore + 1)
							.concat(siblings.slice(startIndexAfter, endIndexAfter + 1));

						nextNavs = nextNavs.concat(itemsToAdd.slice(0, remainingSlots));
						// Put them All Together
						nextNavs = [...nextNavs];
					}
					// Add Parent to Top of List
					nextNavs.unshift(audienceArray[parentIndex]);
				}
				// Logic to Fill out Remaining Spots
				let totalResults = nextNavs.length;
				if (nextNavs.length < linksToShow) {
					for (let i = 0; i <= linksToShow - totalResults; i++) {
						const currentIndex = (parentIndex + i) % audienceArray.length;
						let nav = audienceArray[currentIndex];
						if (
							nav?.url &&
							nav?.title &&
							!this.isCurrentNav(nav) &&
							!nextNavs.find((item) => item?.post_id === nav?.post_id)
						) {
							nextNavs.push(nav);
						}
					}
				}
			}
		}
		if (!nextNavs.length) {
			return;
		}
		// remove duplicates
		nextNavs = CDC.Common.unique(nextNavs);

		this.nodes.related.classList.add('related-pages');

		// default to english
		let relatedPagesText = CDC_Lang.__('Related Pages');
		let topicText =  CDC_Lang.__('View All');

		let html = `
			<div class="related-pages__body">
				<h2 class="related-pages__heading">${relatedPagesText}</h2>
				<ul>
					${nextNavs
			.map(
				(nav) =>{
					if(nav?.exclude?.relatedPages) return;
					return (
						`<li>
							<a class="truncate truncate__60" href="${CDC.cleanAttr(nav.url)}">${nav?.text}</a>
						</li>`
					)
				}
			)
			.join('\n')}
				</ul>
			</div>
		`;
		let homepage_path = this.homepage?.url || this.site?.site_index  || this.site?.path;
		if ( (this.site?.title || this.site?.short_title) && homepage_path) {
			html += `
				<div class="related-pages__footer">
					<a href="${CDC.cleanAttr(audienceHome.url ? audienceHome.url : homepage_path)}">
						<span>${topicText}</span>
						<span>${this.site?.short_title ? this.site.short_title : this.site.title}</span>
					</a>
				</div>
			`;
		}
		$(this.nodes.related).safehtml(html);
		$(this.nodes.related_mobile).safehtml(html);

		// Check for relatedPages module
		if (this.nodes.related) {
			const btn = CDC.make('button');
			btn.classList.add('back-to-top');
			btn.innerHTML += `<span class="cdc-fa-angle-up"></span>`;
			btn.innerHTML += `<span class="back-to-top__info">${CDC_Lang.__('Back to Top')}</span>`;
			// Add scroll to top click event
			btn.addEventListener('click', () => {
				window.scrollTo({top: 0, behavior: 'smooth'})
			});

			this.nodes.related.appendChild(btn);
		}
	}

	renderJourney() {
		if (!this.nodes.journey) {
			return;
		}
		this.nodes.journey.innerHTML = '';

		// Skip navNext if exclude.journey is true
		while (this.navNext && this.navNext.exclude && this.navNext.exclude.journey) {
			let currentIndex = this.flatNav.findIndex(nav => nav === this.navNext);
			this.navNext = this.flatNav[currentIndex + 1];
		}

		if (!this.navNext) {
			return;
		}
		let nav = this.navNext;

		if (nav.audience !== CDC.Page.audience) {
			nav = this.nav[CDC.Page.audience][0];
		}
		if (!nav || nav === this.navCurrent) {
			return;
		}

		//Exclude pages from User Journey navigation
		if(nav?.exclude?.journey) return

		$(this.nodes.journey).safehtml(`
            <a href="${CDC.cleanAttr(nav.url)}" class="cdc-journey-nav">
                <span>${nav?.text}</span>
            </a>
        `);
	}

	// Render alternate language links
	renderLangLinks() {
		// first find target dom element
		let element = document.querySelector('main [data-alt-langs]');
		if (!element) {
			element = document.querySelector('main .cdc-page-title-bar__item--languages');
		}
		if (!element) {
			element = CDC.make('div');
			document.querySelector('.cdc-page-title-bar')?.append(element);
		}

		// build alt langs
		let altLangs = [];
		let langLinks = [];
		if (Array.isArray(this.navCurrent?.alt_langs)) {
			altLangs = altLangs.concat(this.navCurrent.alt_langs)
		}
		// include any alt langs from the page
		// if (CDC.Page.altLangs) {
		// 	CDC.Page.altLangs.forEach(altLang => {
		// 		if (altLang.url && !altLangs.find(item => String(altLang.url).trim() === String(item.url).trim() )) {
		// 			altLangs.push(altLang);
		// 		}
		// 	})
		// }

		// if current nav isn't the exact current page, it's an alt lang candidate
		if (this.navCurrent?.post_id && this.navCurrent.post_id !== CDC.Page.postId) {
			altLangs.push(this.navCurrent)
		}
		// add motionpoint languages if found
		if ('object' === typeof this.site.motionpoint && Object.keys(this.site.motionpoint).length) {
			Object.entries(this.site.motionpoint).forEach(([lang, siteUrl]) => {
				altLangs.push({
					lang,
					url: siteUrl + CDC.parseUrl().pathname,
					post_id: 0,
				})
			})
		}
		if (!altLangs.length) {
			return;
		}

		altLangs.forEach(altLang => {
			altLang = Object.assign({}, altLang);
			let lang = String(altLang.lang);
			let url = String(altLang.url);
			let postId = parseInt(altLang.post_id);
			let label = CDC_Lang.getLabel(lang);
			if (!url || !label || postId === CDC.Page.postId) {
				return;
			}
			langLinks.push({lang, label, url});
		});

		// set up lang links for display
		element.innerHTML = '';
		element.classList.add('cdc-page-title-bar__item')
		element.classList.add('cdc-page-title-bar__item--languages')

		if (!langLinks.length) {
			return;
		}

		// display for 1 link
		if (1 === langLinks.length) {
			let langLink = langLinks[0];
			element.append(
				CDC.make('a', 'cdc-page-title-bar__item', {href: langLink.url, lang: langLink.lang}, langLink.label)
			);
		}
		if (1 < langLinks.length) {
			element.append(
				CDC.make('a', 'nav-link dropdown-toggle', {href: '#', 'data-bs-toggle':'dropdown'}, CDC_Lang.__('Languages'))
			);
			let ul = CDC.make('ul', 'dropdown-menu', {role:'menu'});
			langLinks.forEach(langLink => {
				let li = CDC.make('li');
				let a = CDC.make('a', '', {href: langLink.url, lang: langLink.lang}, langLink.label);
				li.append(a);
				ul.append(li);
			})
			element.append(ul);
		}
	}

	renderBreadcrumb() {
		const titleBar = document.querySelector('.cdc-page-title-bar');
		if (!titleBar) {
			return;
		}
		let breadCrumb = null;
		// group site breadcrumb (not on homepage)
		if (this.site.group_site_short_title && this.site.group_site_url && this.site.site_url
			&& 'cdc_homepage' !== CDC.Page.dfeTemplate
		) {
			breadCrumb = CDC.make('div', 'cdc-page-title-bar__item cdc-page-title-bar__item--breadcrumb breadcrumbs breadcrumbs--group');
			breadCrumb.innerHTML = `
				<span class="breadcrumb breadcrumb--1">
					<a href="${CDC.cleanAttr(this.site.group_site_url)}">${this.site.group_site_short_title}</a>
				</span>
				<span class="breadcrumb breadcrumb--2">
					<a href="${CDC.cleanAttr(this.site.site_url)}">${this.site.short_title || this.site.title}</a>
				</span>
			`;
		}
		// core topic breadcrumb
		if (this.site.core_topic_text && this.site.core_topic_url) {
			breadCrumb = CDC.make('div', 'cdc-page-title-bar__item cdc-page-title-bar__item--breadcrumb breadcrumbs breadcrumbs--core-topic');
			breadCrumb.innerHTML = `
				<span class="breadcrumb breadcrumb--1">
					<a href="${CDC.cleanAttr(this.site.core_topic_url)}">${this.site.core_topic_text}</a>
				</span>
			`;
		}
		if (breadCrumb) {
			titleBar.prepend(breadCrumb);
		}
	}

	updateFocusability() {
		let contents = document.querySelector('.page-toc #contents');
		let overlay = document.querySelector('.read-more-fade');
		if (contents && overlay) {
			let overlayTop = overlay.getBoundingClientRect().top;
			let listItems = document.querySelectorAll('.page-toc #contents li');
			listItems.forEach(li => {
				let liBottom = li.getBoundingClientRect().bottom - parseInt(window.getComputedStyle(li).marginBottom);
				if (liBottom > overlayTop) {
					li.querySelector('a').setAttribute('tabindex', '-1');
				} else {
					li.querySelector('a').removeAttribute('tabindex');
				}
			});
		}
	}

	// renders table of content (multipage menu) if set
	renderTOC() {
		// first see if page is part of a TOC
		if (!this.navCurrent) {
			return;
		}

		let tocNav = null;
		let tocTop = true;
		if (this.navCurrent.settings?.toc_enabled) {
			tocNav = this.navCurrent;
		} else if (this.navCurrent.parent?.settings?.toc_enabled) {
			tocNav = this.navCurrent.parent;
		}
		// no nav, no TOC
		if (!tocNav || !Array.isArray(tocNav.children) || !tocNav.children.length) {
			return;
		}

		this.toc = {
			label: CDC_Lang.__('Table of Contents'),
			title: String( tocNav.settings?.toc_title ).trim() || tocNav.title,
			type: tocNav.settings?.toc_type || 'numbered', // numbered or list
			element: CDC.make('div', 'page-toc', {id: 'toc'}),
			nodes: {},
			nav: tocNav,
			items: tocNav.children,
			isOpen: false,
		};

		// TOC goes top for L1, bottom for L2s
		tocTop = 1 === this.navCurrent.level;

		if (!this.toc.element) {
			this.toc.element = CDC.make('div', 'page-toc');
		}
		this.toc.element.innerHTML = '';

		this.toc.nodes = {
			wrapper: this.toc.element,
			heading: CDC.make('div', 'page-toc__heading'),
			list: CDC.make(('numbered' === this.toc.type) ? 'ol' : 'ul', 'page-toc__list'),
			footer: CDC.make('div', 'page-toc__footer'),
		};
		this.toc.nodes.wrapper.append(this.toc.nodes.heading);
		this.toc.nodes.wrapper.append(this.toc.nodes.list);
		this.toc.nodes.wrapper.append(this.toc.nodes.footer);

		// hide related pages when TOC shows
		this.nodes.related?.setAttribute('hidden', 'hidden');

		// we have a TOC, now find where to render
		if (tocTop) {
			this.toc.element.classList.add('toc-l1');
			if ($('.dfe-section--page-summary:first').length) {
				$('.dfe-section--page-summary:first').after(this.toc.element);
			} else {
				console.error("CDC_Navigation: can't place top TOC");
				return;
			}
		} else {
			this.toc.element.classList.add('toc-l2');
			if (this.nodes.journey) {
				$(this.nodes.journey).after(this.toc.element);
			} else {
				console.error("CDC_Navigation: can't place bottom TOC");
				return;
			}
		}

		// set up heading
		if (tocTop) {
			this.toc.nodes.heading.innerHTML = `${this.toc.label} <span class="title-pipe"> | </span><span class="title-break"><br></span><span class="title-desktop">${this.toc.title}</span>`;
		} else {
			this.toc.nodes.heading.innerHTML = `
				${this.toc.label} <span class="title-pipe"> | </span><span class="title-break"><br></span><a class="heading" href="${CDC.cleanAttr(tocNav.url)}">${this.toc.title}</a>
			`;
		}
		this.toc.nodes.links = [];

		// all links in TOC
		let currentNav = null;
		let currentNavIndex = -1;
		this.toc.items.forEach((nav, index) => {
			let li = CDC.make('li');
			if (nav.active) {
				li.className = 'active';
				currentNavIndex = index;
				currentNav = null;
			}

			let a = CDC.make('a');
			a.href = CDC.cleanAttr(nav.url);
			a.innerHTML = nav.text || nav.title;
			li.appendChild(a);
			this.toc.nodes.links.push(a);
			this.toc.nodes.list.appendChild(li);
		});

		if (!tocTop) {
			let currentPage = (-1 < currentNavIndex) ? currentNavIndex + 1 : 1;
			let pages = this.toc.items.length;

			// sub title
			let pageTitle = document.querySelector('.cdc-page-title');
			if (pageTitle) {
				this.toc.nodes.titleSub = CDC.make('div', 'toc-heading');
				this.toc.nodes.titleSub.innerHTML = `
					<a class="heading" href="${CDC.cleanAttr(tocNav.url)}">${this.toc.title}</a>
					<span class="title-pipe"> | </span>
					<span class="title-break"><br></span>
					${CDC_Lang.__('Page')} ${currentPage} ${CDC_Lang.__('of')} ${pages} <span class="pipe-2"> | </span>
					<a class="all-pages" href="#toc">${CDC_Lang.__('All pages')} <span class="cdc-fa-arrow-down-long"></span></a>
				`;
				pageTitle.append(this.toc.nodes.titleSub);
				this.toc.nodes.titleSub.querySelector('a.all-pages').addEventListener('click', (e) => {
					this.toggleTOC(true);
				})
			}

			let allPages = this.toc.nodes.heading.querySelector('a.all-pages');
			if (allPages) {
				allPages.addEventListener('click', (e) => {
					e.preventDefault();
					this.toggleTOC(true);
				});
			}
		}

		this.toc.nodes.more = CDC.make('a', 'page-toc__more', {href: '#toc'}, CDC_Lang.__('Show More'));
		this.toc.nodes.footer.append(this.toc.nodes.more);
		this.toc.nodes.more.addEventListener('click', (e) => this.toggleTOC());

		// if last link is visible, we're in full mode (no Show more / Show Less)
		let lastLink = this.toc.nodes.links[this.toc.nodes.links.length - 1];
		if (lastLink.offsetLeft < this.toc.nodes.list.clientWidth) {
			this.toc.element.classList.add('page-toc--full');
		}

		// handle keyboard navigation
		this.toc.nodes.links.forEach(link => {
			link.addEventListener('focus', (e) => {
				if (link.offsetLeft > this.toc.nodes.list.clientWidth && !this.toc.isOpen) {
					this.toggleTOC(true);
				}
			})
		})

		this.toggleTOC(false)
	}

	/**
	 *
	 * @param open
	 * @returns {function(): boolean}
	 */
	toggleTOC(open) {
		this.toc.isOpen = ('boolean' === typeof open) ? open : !this.toc.isOpen;
		this.toc.element.classList.toggle('open', this.toc.isOpen);
		this.toc.nodes.more.innerHTML = this.toc.isOpen ? CDC_Lang.__('Show Less') : CDC_Lang.__('Show More');
	};

	toggleAudiences() {
		if ( window.location.href.includes('/about/index.html') ) {
			if ( document.getElementById('dfe-section__nav') ) {
				let audienceCount = [];
				let hideAudiences = false;
				for (let audience of CDCPage.AUDIENCES) {
					if (CDC.Page.navigation.nav[audience]?.length > 0) {
						audienceCount.push(audience);
					}
				}
				if(this.navCurrent.settings?.toc_enabled && this.navCurrent.level == 1 ){
					hideAudiences = true;
				}
				if (audienceCount.length >= 2 && !hideAudiences) {
					let navContainer = document.getElementById('dfe-section__nav');
					let navLinksContainer = document.getElementById('dfe-section__nav-links');
					let navLinksHeader = document.getElementById('dfe-section__nav__header');
					navLinksHeader.innerHTML += `
					<h2>${CDC_Lang.__('More Information') }</h2>
					`;

					for (let audience of audienceCount) {
						navLinksContainer.innerHTML += `
							<a href="${CDC.cleanAttr(this.site?.site_index + '#' + audience)}" class="btn btn-outline-secondary site-index-link">${ this.audienceNames[audience] }</a>
						`;
					}
					navContainer.classList.remove('hide');
				}
			}
		}
	}
}

/**
 * Handles calculating scroll position and progress in 1 spot
 * @TODO: Method to add other listeners to throttled scroll progress
 * @TODO: General methods/events to trigger at certain scroll %age/direction
 *
 * window.CDC.ScrollProgress
 */
class CDCScrollProgress {

	elements = {};

	touchStartY = 0;
	touchEndY = 0;

	scrolling = false;
	lastScrollPosition = 0;

	constructor() {
		this.elements = {
			siteHeader: document.querySelector( '.cdc-header' ),
			mobileTitle: document.querySelector( '.cdc-header-mobile__title' ),
			mobileHeader: document.querySelector( '.cdc-header-mobile' ),
			userJourneyMobile: document.querySelector( '.user-journey__mobile' ),
			userJourneyWrapper: document.querySelector( '.user-journey__wrapper' ),
			progressContainer: document.querySelector( '.cdc-page-progress-bar' ),
			progressScrubber: document.querySelector( '.cdc-page-progress-bar__scrubber' ),
			toTopButton: CDC.Page?.getElement('toTopButton'),
		}

		// page without progress or toTop is an outlier, stop here
		if (!this.elements.progressContainer){
			return;
		}
		// pages less than 1500 scrollHeight, also an outlier
		else if (document.body.scrollHeight < 1500) {
			return;
		}

		//resize likely changes scroll %age
		window.addEventListener( 'resize', (event) => this.resize(event) );

		// determine the scroll or swipe direction in order to display things in mobile
		document.addEventListener( 'wheel', (event) => this.getScrollDirection(event) );
		document.addEventListener( 'touchstart', e => {
			this.touchstartY = e.changedTouches[ 0 ].screenY;
		} );
		document.addEventListener( 'touchend', e => {
			this.touchendY = e.changedTouches[ 0 ].screenY;
			if(this.touchendY < this.touchstartY){
				this.logDirection('down','swipe');
			}else if(this.touchendY > this.touchstartY){
				this.logDirection('up','swipe');
			}
		} );

		// scrolling
		// Need to throttle/debounce, maybe?
		window.addEventListener( 'scroll', () => {
			this.lastScrollPosition = window.scrollY;
			if(!this.scrolling){
				window.requestAnimationFrame(() => {
					this.scrollProgress();
					this.scrolling = false;
				})
				this.scrolling = true;
			}
		});

		this.currentScrollY = 0;
		this.lastScrollY = 0;

		setTimeout(() => {
			this.adjustHeaderSpacers();
			this.initialScrollY = window.pageYOffset + this.elements.mobileTitle.getBoundingClientRect().top;
			this.targetScrollY = this.initialScrollY + this.elements.mobileTitle.scrollHeight;
			this.stickyHeaderHandler();
		}, 50)
	}

	get() {
		let winScroll = document.body.scrollTop || document.documentElement.scrollTop,
		height = document.documentElement.scrollHeight - document.documentElement.clientHeight,
		scrolled = ( winScroll / height ) * 100;

		return parseInt(Math.floor(scrolled));
	}

	logDirection(direction,type){
		// console.log( direction, type );
	}

	// checking scroll direction
	getScrollDirectionIsUp(evt) {
		if ( evt.wheelDelta ) {
			return 0 < evt.wheelDelta; // > 0;
		}
		return 0 > evt.deltaY;	// < 0;
	}

	getScrollDirection(evt){
		if ( this.getScrollDirectionIsUp( evt ) ) {
			this.logDirection( 'up', 'scroll' );
		} else {
			this.logDirection( 'down', 'scroll' );
		}
	};

	//handle sticky header
	stickyHeaderHandler() {
		this.currentScrollY = document.documentElement.scrollTop;
		// console.log('this.currentScrollY: ', this.currentScrollY);									1
		// console.log('this.targetScrollY: ', this.targetScrollY);

		// Readies the sticky header to display but tucks it away with CSS
		// console.log('this.currentScrollY: ', this.currentScrollY)
		// console.log('this.targetScrollY: ', this.targetScrollY)

		if (this.currentScrollY > this.initialScrollY) {
			this.elements.mobileHeader?.classList.add('title-engaged');
		} else {
			this.elements.mobileHeader?.classList.remove('title-engaged');
		}

		if (this.currentScrollY > this.targetScrollY) {
			this.elements.mobileHeader?.classList.add('title-disengaged');
		} else {
			this.elements.mobileHeader?.classList.remove('title-disengaged');
		}

		// Displays the sticky header
		if (this.currentScrollY > this.targetScrollY && this.currentScrollY <= this.lastScrollY) {
			this.elements.mobileHeader?.classList.add('title-active');
		} else {
			this.elements.mobileHeader?.classList.remove('title-active');
		}

		this.lastScrollY = this.currentScrollY;
		// console.log('this.lastScrollY: ', this.lastScrollY);
	};

	// when scrolling, set the progress bar and top toTopButton radial
	scrollProgress() {
		let scrolled = this.get();

		// progress bar at top
		this.adjustProgressBar(scrolled);

		// --progress-value is a CSS variable set in totop.scss; updating this will update the radial
		document.documentElement.style.setProperty( '--progress-value', scrolled + '%' );
		// this.adjustTopButtonDisplay(scrolled);

		// Show and hide the mobile version of the User Journey
		// WARN: Don't use these values, it is supposed to be based on position within content area
		// Shown at 75% of the content body (not 75% of the full page), slides up.   Disappears (slides down) before user gets to the real “user journey” link within the body of the page.
		// NOTE: I'd rather this was done another way
		if( CDC.Viewport.isMobile() ) {
			if( null !== this.elements.userJourneyMobile ) {
				if ( 76 > scrolled && 45 < scrolled ) {
					this.elements.userJourneyMobile.classList.remove( 'user-journey__mobile-hidden' );
				} else {
					this.elements.userJourneyMobile.classList.add( 'user-journey__mobile-hidden' );
				}

				// ANOTHER NOTE: just hiding the wrapper isn't idea since the element should use its CSS transitions to hide and show (please don't use JS to do that)
				if ( 77 < scrolled ) {
					this.elements.userJourneyWrapper.classList.remove('d-block');
				} else {
					this.elements.userJourneyWrapper.classList.add('d-block');
				}
			}
		}

		// if( CDC.Viewport.isDesktop() ) {
		// 	this.elements.userJourneyWrapper?.classList.remove('d-block');

		// 	// 508 fix: Add some type of indicator once user has scrolled 100%
		// 	if (scrolled == 100) {
		// 		this.elements.toTopButton.classList.add('is-bottom');
		// 	} else {
		// 		this.elements.toTopButton.classList.remove('is-bottom')
		// 	}
		// }

		this.stickyHeaderHandler();
	};

	resize() {
		// this.adjustTopButtonDisplay(this.get());
		this.scrollProgress();
		this.adjustHeaderSpacers();
	}

	adjustHeaderSpacers(){
		let global = this.elements.mobileTitle?.offsetHeight || 0;
		document.documentElement.style.setProperty('--mobile-header-offset', `${global}px`);
	}

	adjustProgressBar(scrolled) {
		if ( 5 < scrolled ) {
			this.elements.progressContainer?.classList.remove( 'd-none' );
			this.elements.progressScrubber.style.width = scrolled + '%';
		} else {
			this.elements.progressContainer?.classList.add( 'd-none' );
		}
	}

	// adjustTopButtonDisplay(scrolled) {
	// 	if (!CDC.Viewport.isMobile()){
	// 		if ( 60 < scrolled ) {
	// 			this.elements.toTopButton?.classList.add('d-block');
	// 		} else {
	// 			this.elements.toTopButton?.classList.remove('d-block');
	// 		}
	// 	} else {
	// 		// top button radial, should not appear in mobile
	// 		this.elements.toTopButton?.classList.remove('d-block');
	// 	}
	// }
}


/**
 * Encapsulates logic for header search
 */
class CDCSearch {
	constructor() {
		this.currentTerm = '';
		this.currentResults = [];
		this.siteLimit = null;
		this.searchResultsUrl = CDC.Common.cleanString( window.CDC_CONFIG?.search_url || 'https://search.cdc.gov/search/' );
		this.searchTypeaheadSolr = CDC.Common.cleanString( window.CDC_CONFIG?.search_typeahead || 'https://search.cdc.gov/srch/internet_autocomplete/autocomplete' );
		this.typeaheadEnabled = (false !== CDC.Page.config.search_typeahead);

		this.searchCompletes = [];
		this.init();
	}

	init() {
		this.desktop = document.querySelector('header form.cdc-header__search');
		this.mobile = document.querySelector('form#cdc-mobile-search');
		this.mobileSearch = document.querySelector('form#cdc-mobile-search .btn--search');
		this.skipBtn = document.querySelector('#skipmenu a[href="#cdc-search"]');

		// mobile search
		if (this.mobile && this.mobileSearch) {
			this.mobileSearch.addEventListener('click', () => this.mobile.submit());
		}

		// update search results page
		if (this.searchResultsUrl) {
			if ('es' === CDC?.Page?.lang) {
				this.searchResultsUrl += 'spanish/';
			}
		}

		// init search fields
		document.querySelectorAll('form [data-search-input]').forEach(input => {
			this.searchCompletes.push(new CDCSearchField(input, this));
		});

		// 508 fix - Skip to search button
		this.skipBtn?.addEventListener('click', (event) => {
			this.activateSearch();
		});

		// init standard desktop form
		if (this.desktop) {
			this.nodes = {
				searchToggle: this.desktop.querySelector('#cdc-search__toggle'),
				searchInput: this.desktop.querySelector('#cdc-search__input'),
				searchGroup: this.desktop.querySelector('.input-group'),
				searchClear: this.desktop.querySelector('#cdc-search__clear'),
				searchSubmit: this.desktop.querySelector('#cdc-search__submit'),
				searchComplete: this.desktop.querySelector('.cdc-search-complete'),
				searchCompleteResults: [],
				localSearch: document.querySelector('.cdc-header [data-local-search]'),
			};

			this.nodes.searchClear?.addEventListener( 'click', (e) => {
				this.nodes.searchInput.value = '';
				this.desktop.classList.remove('cdc-header__search--active');
				this.currentResults = [];
				this.nodes.searchComplete.innerHTML = '';
			} );

			this.nodes.searchToggle?.addEventListener( 'click', (e) => {
				e.preventDefault();
				this.desktop.classList.add('cdc-header__search--active');
				this.nodes.searchInput.focus();
			} );

			// local site search
			if (this.nodes.localSearch) {
				this.desktop.append(this.nodes.localSearch);
				document.querySelector('#cdc-mobile-search')?.append(this.nodes.localSearch.cloneNode(true));
				if (this.nodes.localSearch.value) {
					this.siteLimit = this.nodes.localSearch.value;
				}
			} else {
				this.siteLimit = this.desktop.querySelector('input[name="sitelimit"]')?.value;
			}
		}
		this.deepLinkCheck();
	}

	activateSearch() {
		this.desktop.classList.add('cdc-header__search--active');
		this.nodes.searchInput.focus();
	}
	  // Function to check if text is found in an element
	isTextFoundInElement(element, text) {
		if (element) {
			let elementText = element.textContent || element.innerText;
			return elementText.includes(text);
		}
		return false;
	}

	deepLinkCheck(){
		// must have come from the CDC search page
		if (!String(document.referrer || '').match('search')) {
			return;
		}
		let cookieName = "cdc-search-text";
		let cookieValue = CDC.Common.getCookie( cookieName );
		if( !cookieValue ) {
			return;
		}
		// Remove Cookie After Scroll
		document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=.cdc.gov; path=/;";

		let countMap = new Map();
		let splitQuery = String(cookieValue).split(' ');
		if ( 1 >= splitQuery.length ) {
			return;
		}
		for (let i=0; i<splitQuery.length - 1; i++) {
			let bigram = splitQuery[i] + ' ' + splitQuery[i+1];
			$('body *:contains(' + bigram + ')').not('script').filter(':visible').filter(function() {
				return 1 > $(this).children('*:contains('+ bigram + ')').length;
			}).each(function(index, element) {
				if (countMap.get(element)) {
					countMap.set(element,countMap.get(element) + 1);
				} else {
					countMap.set(element,1);
				}
			});
		}
		let maxCount = 0;
		let maxElement = '';
		countMap.forEach(function(value,key) {
			if (value > maxCount) {
				maxCount = value;
				maxElement = key;
			}
		})
		// Look for ancestor elements to catch block titles?
		// Highlight text?
		if ( 0 >= maxCount ) {
			return;
		}

		// Skip Scrolling if the text is found in the footer
		let footer = document.querySelector('section.site-footer');
		let skip = this.isTextFoundInElement(footer, maxElement.innerText);
		if (skip) {
			return;
		}

		let style = window.getComputedStyle(maxElement, null).getPropertyValue('font-size');
		let fontSize = parseFloat(style);
		// Get the bounding rectangle of the element
		const rect = maxElement.getBoundingClientRect();
		// Get the current scroll position
		const scrollTop = window.scrollY || document.documentElement.scrollTop;
		// Get the total height of the main content
		const docHeight = document.documentElement.scrollHeight;
		// Calculate the position of the element relative to the entire document
		const elementTop = rect.top + scrollTop;
		// Calculate the 80% mark of the document
		const eightyPercent = docHeight * 0.8;
		// Check if the element is below the 80% mark
		if (elementTop < eightyPercent) {
			// Scroll to the element
			$([document.documentElement, document.body]).animate({
			scrollTop: $(maxElement).offset().top - fontSize*3
			}, 500);
		}
	}


}

// Search field class, handles autocomplete
class CDCSearchField {
	// nodes
	nodes = {
		form: null,
		searchComplete: null,
	};
	// parent CDCSearch instance
	search = null;
	isOpen = false;
	typeaheadEnabled = true;

	constructor(element, searchObj) {
		this.element = element;
		this.search = searchObj;
		if (!this.element) {
			CDC.debug && console.error('CDCSearchComplete: no element found', this.element);
			return;
		}

		// carry over config
		this.searchTypeaheadSolr = this.search.searchTypeaheadSolr;
		this.searchResultsUrl = this.search.searchResultsUrl;
		this.typeaheadEnabled = this.search.typeaheadEnabled;
		if ('off' === this.element.dataset['searchComplete']) {
			this.typeaheadEnabled = false;
		}

		// parent form must be present
		this.nodes.form = this.element.closest('form');
		if (!this.nodes.form) {
			CDC.debug && console.error('CDCSearchComplete: no parent form', this.element);
			return;
		}

		// initialize a typeahead element only once
		if (this.element.dataset.init) {
			return;
		}

		// manually update search form if search results url is different
		if (!this.nodes.form.getAttribute('action')?.includes(this.searchResultsUrl)) {
			this.nodes.form.setAttribute('action', this.searchResultsUrl);
		}

		this.element.autocorrect = 'off';
		this.element.spellcheck = false;

		if (this.typeaheadEnabled) {

			// disable native autocomplete
			this.element.autocomplete = 'off';

			if (!this.nodes.searchComplete) {
				this.nodes.searchComplete = CDC.Common.make('div', 'cdc-search-complete');
				this.element?.after(this.nodes.searchComplete);
			}

			if (this.nodes.searchComplete && this.element && 'en' === CDC.Page?.lang) {
				this.onQueryUpdate = CDC.Common.debounce(() => this.onQuery(), 300);
				this.element.addEventListener('input', () => this.onQueryUpdate());
				this.element.addEventListener('keydown', (e) => this.onCompleteKey(e))
				this.nodes.searchComplete.addEventListener('keydown', (e) => this.onCompleteKey(e))

				this.nodes.form.addEventListener('blur', () => this.toggleComplete(false));
				window.document.addEventListener('focus', (e) => {
					if (this.isOpen && !this.nodes.form.contains(e.target)) {
						this.toggleComplete(false)
					}
				});
				window.document.addEventListener('click', (e) => {
					if (this.isOpen && !this.nodes.form.contains(e.target)) {
						this.toggleComplete(false)
					}
				});
			}
		}
	}

	onQuery() {
		let newTerm = this.cleanTerm(this.element.value).toLowerCase();
		let oldTerm = this.currentTerm;
		this.currentTerm = newTerm;
		if (!newTerm) {
			this.toggleComplete(false);
		}

		if (newTerm.length < 2) return;

		if (oldTerm === newTerm) {
			return;
		}
		$.ajax({
			method: 'get',
			url: this.searchTypeaheadSolr,
			data: {
				q: this.currentTerm,
				wt: 'json',
				rows: 5,
				fl: 'autocomplete_search_term',
			},
			dataType: 'json',
		}).then((response) => {
			let results = [].concat(response?.response?.docs).map(result => result.autocomplete_search_term);
			this.onQueryResults(results);
		})
	}

	onCompleteKey(e) {
		switch (e.key) {
			case 'ArrowDown':
				e.preventDefault();
				return this.onCompleteNav(e, 1);
			case 'Tab':
				if (this.isOpen) {
					e.preventDefault();
					return this.onCompleteNav(e, 1);
				}
				break;
			case 'ArrowUp':
				e.preventDefault();
				return this.onCompleteNav(e, -1);
			case 'Escape':
				this.element.focus();
				return this.toggleComplete(false);
		}
	}

	// move up or down suggestions
	onCompleteNav(event, index) {
		if (!this.isOpen) {
			return;
		}
		let cancel = false;
		const el = event.target;
		if (!this.nodes.searchComplete.contains(el)) {
			this.nodes.searchCompleteResults[0]?.focus();
			cancel = true;
		} else {
			let lastResultIndex = this.nodes.searchCompleteResults.length - 1;
			let resultIndex = this.nodes.searchCompleteResults.indexOf(el);
			let newResultIndex = resultIndex + index;
			if (0 > newResultIndex) {
				newResultIndex = lastResultIndex;
			} else if (lastResultIndex < newResultIndex) {
				newResultIndex = 0;
			}
			this.nodes.searchCompleteResults[newResultIndex]?.focus();
			cancel = true;
		}

		if (cancel) {
			event.preventDefault();
		}

	}

	onQueryResults(results) {
		results = Array.isArray(results) ? results.slice(0, 5) : [];
		this.currentResults = results;
		this.nodes.searchComplete.innerHTML = '';

		const topResultsText = CDC.Common.make('div', '', {}, 'TOP RESULTS');
		topResultsText.classList.add('topresults');
		this.nodes.searchComplete.append(topResultsText);

		this.nodes.searchCompleteResults = [];
		if (results.length) {
			results.forEach(result => {
				result = this.cleanTerm(result);
				if (!result) {
					return;
				}
				let url = `${this.searchResultsUrl}?query=${result}`;
				if (this.search?.siteLimit) {
					url += `&sitelimit=${this.search.siteLimit}`;
				}
				const highlightedResult = result.replace(new RegExp(`(${this.currentTerm})`, 'gi'), '<b>$1</b>');
				const a = CDC.Common.make('a', 'cdc-search-complete__result', { href: url }, highlightedResult);
				this.nodes.searchComplete.append(a);
				this.nodes.searchCompleteResults.push(a);
				a.addEventListener('click', () => {
					window.location = url;
				});
				a.addEventListener('keyup', (e) => {
					if ('Enter' === e.key) {
						window.location = url;
					}
				});
			});
		}
		this.toggleComplete(results.length);
	}

	toggleComplete(onoff) {
		this.nodes.searchComplete.classList.toggle('show', !!onoff);
		this.nodes.form.classList.toggle('search-menu-open', !!onoff);
		document.body.classList.toggle('search-overlay-active', !!onoff);
		this.isOpen = !!onoff;
	}

	cleanTerm(term) {
		return CDC.Common.cleanString(String(term).trim().replace(/["|;&$%#<>()+\?\~\*]/g, ''));
	}
}

// if there's a carousel on the page, set the tabindex to -1 to any buttons which aren't on the active slide
// NOTE: this might need to be expanded into other focusable elements
document.addEventListener( 'DOMContentLoaded', () => {
	const carousels = document.querySelectorAll( '.carousel' );
	carousels.forEach( carousel => {
		const setTabIndex = () => {
			carousel.querySelectorAll( '.carousel-item a.btn' ).forEach( btn => {
				btn.setAttribute( 'tabindex', btn.closest( '.carousel-item' ).classList.contains( 'active' ) ? '0' : '-1' );
			} );
		};
		setTabIndex();
		carousel.addEventListener( 'slid.bs.carousel', setTabIndex );

		// Make indicators tabbable
		carousel.querySelectorAll( '.carousel-indicators [data-bs-slide-to]' ).forEach( indicator => {
			indicator.setAttribute( 'tabindex', '0' );
		} );
	} );
} );

/**
 * Logic for specific DFE / Page Templates
 */
class CDCTemplates {

	dfeTemplate = null;

	constructor() {
		this.init();
	}

	init() {
		// grab from CDC.Page object
		this.dfeTemplate = CDC.Page.dfeTemplate;

		// run DFE template specific logic
		switch (this.dfeTemplate) {
			case 'cdc_sitemap':
				CDC.Page.on('navLoaded', (e) => this.siteIndex());
				break;
			case 'cdc_outbreak_homepage':
				this.outbreakHomepage();
				break;
			case 'cdc_events':
				this.loadIcs();
				break;
		}
	}

	// site index page
	siteIndex() {
		const pageContent = document.querySelector('.cdc-find-information');
		const audiences = document.querySelectorAll('.cdc-dfe-sitemap__panes h2');
		const {
			sub_site_list_link:subSiteListLink,
			group_site_short_title: groupSiteShortTitle,
			group_site_spanish_short_title: groupSiteSpanishShortTitle,
			sub_site_spanish_list_link: subSiteSpanishListLink,
			super_site_enabled: superSiteEnabled
		} = CDC.Page.navigation.site;

		let link = subSiteListLink;
		let linkText = 'View all';
		let title = groupSiteShortTitle;

		if (CDC.Page.isSpanish && '' !== subSiteSpanishListLink) {
			link = subSiteSpanishListLink;
			title = groupSiteSpanishShortTitle;
			//for translation purposes
			linkText = 'View All';
		}

		// Audience links
		let audienceLinks = '';
		for (let audience of audiences) {
			let audienceTitle = audience.textContent;
			const audienceValue = audience.id;
			audienceLinks += `<a href="#${audienceValue}" class="btn btn-outline-secondary">${audienceTitle} <i class="cdc-fa-arrow-down-long"></i></a>`;
		}

		if ( (!superSiteEnabled  && 1 < audiences.length) || superSiteEnabled ) {
			pageContent?.prepend(
				CDC.make('div', 'dfe-section dfe-section--page-summary', {}, `
					<div class="site-index-info">
						<div class="dfe-section__header">
							<h2>${CDC_Lang.__('Find Information')}</h2>
						</div>
						<div class="dfe-section__content">
							<div class="d-flex flex-sm-row flex-column align-items-start">
								${ audienceLinks }
							</div>
						</div>
					</div>
					${link ?
						`<div class="site-index-info-link">
							<a href="${link}"> ${CDC_Lang.__(linkText)} ${title} ${CDC_Lang.__('pages')}
								<i class="cdc-fa-light cdc-fa-angle-right" role="img" aria-hidden="true"></i>
							</a>
							</div>
						`:''
					}
				`)
			)
		}
	}

	// outbreak homepage - render summary links
	outbreakHomepage() {
		const summaryButtons = document.querySelector('.dfe-section--page-summary .dfe-section__content');
		const feedLinks = document.querySelectorAll('.dfe-section--feed .onThisPageAnchor');
		if (summaryButtons && feedLinks.length) {
			feedLinks.forEach(anchor => {
				const title = CDC.Common.stripTags(anchor.getAttribute('title'));
				const id = anchor.getAttribute('id');
				if (title && id) {
					summaryButtons.append(
						CDC.make('a', 'btn btn-outline-blue', {href: `#${id}`}, title)
					);
				}
			})
		}
	}

	loadIcs() {
		let link = document.querySelector(".add2_calendar a");
		if (!CDC_POST.event || !link) {
			return;
		}

		link.href = this.makeIcsFile();
		link.download = "event.ics";
		link.removeAttribute('hidden');
	}

	makeIcsFile() {

		const convertTo24Hour = (time12h) => {
			const [time, modifier] = time12h.split(' ');
			let [hours, minutes] = time.split(':').map(Number);

			if (hours === 12) {
				hours = 0;
			}

			if (modifier === 'PM') {
				hours += 12;
			}

			return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
		}

		const convertToIcsDate = (dateString) => {
			let date = new Date(dateString);
			let year = date.getUTCFullYear();
			let month = ("0" + (date.getUTCMonth() + 1)).slice(-2); // Months are 0 based
			let day = ("0" + date.getUTCDate()).slice(-2);
			let hours = ("0" + date.getUTCHours()).slice(-2);
			let minutes = ("0" + date.getUTCMinutes()).slice(-2);
			let seconds = ("0" + date.getUTCSeconds()).slice(-2);

			return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
		}

		const formatDate = (date) => {
			// Ensure the input is a Date object
			if (!(date instanceof Date)) {
				throw new Error("Invalid Date");
			}
			const pad = (num) => String(num).padStart(2, '0');

			const year = date.getFullYear();
			const month = pad(date.getMonth() + 1);
			const day = pad(date.getDate());
			const hours = pad(date.getHours());
			const minutes = pad(date.getMinutes());
			const seconds = pad(date.getSeconds());

			return `${year}${month}${day}T${hours}${minutes}${seconds}`;
		}

		let event = CDC_POST.event;
		let eventStartDate = event.startDate;
		let eventTimeZone = event.tz?.toLowerCase();

		let timeZoneString;
		switch (eventTimeZone) {
			case 'et':
				timeZoneString = 'America/New_York';
				break;
			case 'ct':
				timeZoneString = 'America/Chicago';
				break;
			case 'mt':
				timeZoneString = 'America/Denver';
				break;
			case 'pt':
				timeZoneString = 'America/Los_Angeles';
				break;
			case 'ak':
				timeZoneString = 'America/Anchorage';
				break;
			case 'hi':
				timeZoneString = 'America/Los_Angeles';
				break;
			default:
				timeZoneString = 'Pacific/Honolulu';
		}

		let eventStartTime = convertTo24Hour(event.startTime);
		let tmpSDate = new Date(eventStartDate);
		eventStartDate = tmpSDate.toISOString().split('T')[0];
		let eventStartGMT = formatDate(new Date(eventStartDate + 'T' + eventStartTime))
		let eventEndDate = event.endDate;
		let eventEndTime = convertTo24Hour(event.endTime);
		tmpSDate = new Date(eventEndDate);
		eventEndDate = tmpSDate.toISOString().split('T')[0];
		let eventEndGMT = eventEndDate ? formatDate(new Date(eventEndDate + 'T' + eventEndTime)) : '';
		let createdGMTTime = convertToIcsDate(new Date().toISOString());
		let address1 = event.location.address1;
		let address2 = event.location.address2;
		let city = event.location.city;
		let state = event.location.state;
		let postalCode = event.location.zip;
		let uid = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
		let summary = event.title || '';
		let content = event.description || '';
		let addressArr = [];

		if (address1) {
			addressArr.push(address1);
		}
		if (address2) {
			addressArr.push(address2);
		}
		if (city) {
			addressArr.push(city);
		}
		if (state) {
			addressArr.push(state);
		}
		if (postalCode) {
			addressArr.push(postalCode);
		}

		let locationStr = addressArr.length ? addressArr.join(' ') : '';
		locationStr = locationStr.replace(/"/g, '\\"');

		let icsData =
			"BEGIN:VCALENDAR\n" +
			"PRODID:-//CDC//WCMS//EN\n" +
			"VERSION:2.0\n" +
			"METHOD:PUBLISH\n" +
			"X-MS-OLK-FORCEINSPECTOROPEN:TRUE\n" +
			"BEGIN:VEVENT\n" +
			"CLASS:PUBLIC\n" +
			"CREATED:" + createdGMTTime + "\n" +
			"DTSTAMP:" + createdGMTTime + "\n" +
			"DTSTART;TZID=" + timeZoneString + ":" + eventStartGMT + "\n" +
			(eventEndDate ? "DTEND;TZID=" + timeZoneString + ":" + eventEndGMT + "\n" : "") +
			"LAST-MODIFIED:" + createdGMTTime + "\n" +
			(locationStr ? "LOCATION:" + locationStr + "\n" : "") +
			"DESCRIPTION:" + content + "\n" +
			"X-ALT-DESC;FMTTYPE=text/html:" + summary + "\n" +
			"SUMMARY:" + summary + "\n" +
			"TRANSP:OPAQUE\n" +
			"UID:" + uid + "\n" +
			"URL:" + event.permalink + "\n" +
			"END:VEVENT\n" +
			"END:VCALENDAR\n";

		let data = new File([icsData], {type: "text/plain"});

		if (this.icsFile !== null) {
			window.URL.revokeObjectURL(this.icsFile);
		}

		this.icsFile = window.URL.createObjectURL(data);

		return (this.icsFile);
	}

}

/**
 * Viewport object
 * Concerned with determining properties of current viewport
 * NOTE: These values are provided through media queries, don't use JS to calculate
 * @TODO: Set breakpoint at certain times to prevent unneeded selections and reads. At call time, at load, on resize?
 *
 * CDC.Viewport
 */
class CDCViewport{
	constructor(){}

	/**
	 * Gets viewport size and value. ex. "xs,1"
	 * @returns string
	 */
	getBreakpoint() {
		return getComputedStyle( document.querySelector( 'html' ), ':before' ).getPropertyValue( 'content' );
	}

	/**
	 * Get the value of viewport size
	 * @returns int
	 */
	getBreakpointValue() {
		return parseInt( this.getBreakpoint().split( ',' )[ 1 ] );
	}

	/**
	 * True when considered mobile sized viewport
	 * @returns bool
	 */
	isMobile() {
		return ( 2 > parseInt( this.getBreakpointValue() ) );
	}

	/**
	 * True when considered desktop sized viewport - generally !isMobile, but maybe not always
	 * @returns bool
	 */
	isDesktop() {
		return ( 2 < parseInt( this.getBreakpointValue() ) );
	}
}

CDC.Viewport = new CDCViewport();

/**
 * Base utilties and entry point for final output file
 * window.CDC.Page.getElement( 'element_name' )
 * window.CDC.Page.debug(arg1,arg2,arg3,...);
 */
class CDCPage {
	static ENGLISH = 'en';
	static SPANISH = 'es';

	static AUDIENCE_GEN = 'gen';
	static AUDIENCE_HCP = 'hcp';
	static AUDIENCE_PHP = 'php';
	static AUDIENCES = [CDCPage.AUDIENCE_GEN, CDCPage.AUDIENCE_HCP, CDCPage.AUDIENCE_PHP];

	elements = {};
	lang = CDCPage.ENGLISH;
	postId = 0;
	siteId = 0;
	context = '';
	pid = '';
	audience = CDCPage.AUDIENCE_GEN;
	tax = {};
	altLangs = [];
	config = {};
	// is syndicated content?
	syndicated = false;

	// track DFE template
	dfeTemplate = null;

	constructor() {
		// eslint-disable-next-line no-undef
		this.events = new CDCEvents();
		this.on = (eventName, callback) => this.events.on(eventName, callback);
		this.once = (eventName, callback) => this.events.once(eventName, callback);
		this.emit = (eventName, data) => this.events.emit(eventName, data);
		// on window load, page initiates
		window.addEventListener('load', () => {
			this.init();
		});

		document.addEventListener('DOMContentLoaded', function () {
			const alphabetLinks = document.querySelectorAll('.atoz-characters li a');

			alphabetLinks.forEach(function (link) {
				// Extract the letter from the href attribute, e.g., "#heading-a" becomes "a"
				const letter = link.getAttribute('href').replace('#heading-', '');

				// Look for an element with the ID corresponding to this letter
				const element = document.getElementById('heading-' + letter);

				if (element) {
					// If the element with the ID exists, enable the link
					link.classList.remove('disabled-link');
					link.classList.add('enabled');
					link.setAttribute('aria-label', `Link to ${letter.toUpperCase()}`);
				}

				// Add event listener for click to handle selection
				link.addEventListener('click', function (event) {
					// Remove 'selected' class from all links
					alphabetLinks.forEach(function (l) {
						l.classList.remove('selected');
					});
					// Add 'selected' class to the clicked link
					link.classList.add('selected');
				});
			});
		});
	}

	/**
	 * Address elements that may be used across modules, so they are found once and can be referenced later
	 * These should be elements on nearly every page
	 */
	init() {
		this.elements = {
			toTopButton: document.querySelector('.cdc-page-to-top'),
			otp: document.querySelector('.on-this-page.show'),
		};

		this.emit('init');

		// no js remove
		document.body?.classList?.remove('no-js');

		// gather page properties (language, site ID, post ID...)
		this.loadProperties();

		// load all page features
		try {
			this.loadFeatures();
		} catch (e) {
			console.error('Failed loading features:', e);
		}

		// attach UI event handlers
		this.attachEvents();

		// check for page modules to load
		// eslint-disable-next-line no-undef
		CDCModules.load();

		this.emit('ready');

		// avoid second calls
		this.init = false;
	}

	// test if page is English
	get isEnglish() {
		return this.lang === CDCPage.ENGLISH;
	}

	// test if page is English
	get isSpanish() {
		return this.lang === CDCPage.SPANISH;
	}

	// load page properties
	loadProperties() {
		// get language
		let lang = String(document.querySelector('html')?.getAttribute('lang') || 'en')
			.trim()
			.toLocaleLowerCase();
		if (lang) {
			switch (lang) {
				case 'es-us':
				case 'es':
					this.lang = CDCPage.SPANISH;
					break;
				case 'en-us':
				case 'en':
					this.lang = CDCPage.ENGLISH;
					break;
				default:
					this.lang = lang.replace(/^.*\-/, '');
			}
		}

		// pull page CDC_POST page var
		if ('object' === typeof window.CDC_POST) {
			this.pid = String(window.CDC_POST.id || '').trim();
			[this.siteId, this.postId] = this.pid.split(/[\-\_]+/).map((val) => parseInt(val));
			this.tax = Object.assign(this.tax, window.CDC_POST.tax);
			this.lang = this.lang || window.CDC_POST.lang;
			this.context = window.CDC_POST.context;
			if (window.CDC_POST.alt_langs) {
				this.altLangs = this.altLangs.concat(window.CDC_POST.alt_langs);
			}
			if (CDCPage.AUDIENCES.includes(window.CDC_POST.audience)) {
				this.audience = window.CDC_POST.audience;
			}
			this.type = window.CDC_POST.type;
		}

		// pull in site config
		this.config = Object.assign({}, this.config, window.CDC_CONFIG);

		// get dfe template
		this.dfeTemplate =
			document.querySelector('meta[property="cdc:dfe_content_type"]')?.getAttribute('content') || null;

		// syndicated?
		this.syndicated = document.body?.classList?.contains('syndicated-content');
	}

	// load common features
	loadFeatures() {
		// uswds gov banner
		try {
			// eslint-disable-next-line no-undef
			this.uswdsBanner = new USWDSBanner();
		} catch (e) {
			console.error(e);
		}

		// header menu
		try {
			// eslint-disable-next-line no-undef
			this.topMenu = new CDCTopMenu();
		} catch (e) {
			console.error(e);
		}

		// header mobile menu
		try {
			// eslint-disable-next-line no-undef
			this.mobileMenu = new CDCMobileMenu();
		} catch (e) {
			console.error(e);
		}

		// header search
		try {
			// eslint-disable-next-line no-undef
			this.search = new CDCSearch();
		} catch (e) {
			console.error(e);
		}

		// footer menu
		try {
			// eslint-disable-next-line no-undef
			this.bottomMenu = new CDCBottomMenu();
		} catch (e) {
			console.error(e);
		}

		// scroll progress
		try {
			// eslint-disable-next-line no-undef
			this.scrollProgress = new CDCScrollProgress();
		} catch (e) {
			console.error(e);
		}

		// navigation
		try {
			// eslint-disable-next-line no-undef
			this.navigation = new CDCNavigation();
		} catch (e) {
			console.error(e);
		}

		// template specific features
		try {
			// eslint-disable-next-line no-undef
			this.templates = new CDCTemplates();
		} catch (e) {
			console.error(e);
		}

		// common page components
		try {
			// eslint-disable-next-line no-undef
			this.features = new CDCFeatures();
		} catch (e) {
			console.error(e);
		}
	}

	attachEvents() {
		// load // document.addEventListener('DOMContentLoaded', {});
		// `DOMContentLoaded` event is fired when the main document has been loaded and parsed, but before all of the resources (images, iframes, scripts, etc.) have finished loading. The `load` event is fired when the entire page has finished loading, including all resources.

		// window.addEventListener( 'load', () => {
		// 	this.debug( 'Current VP', window.CDC.Viewport.getBreakpoint() );
		// } );
		this.positionOTP(true);

		// WARN: resize event listener also appears in scroll-progress JS, need to limit these listeners
		window.addEventListener('resize', () => {
			this.positionOTP(false);
		});
	}

	// WARN: don't leave this here.
	// NOTE: this is to align the OTP module with the first paragraph in the content (per UX)
	// SIDE NOTE: this will cause a little jump when the calculation is finished, it might be better to keep the OTP hidden until after it is repositioned, then show it.
	positionOTP(isFirstLoad) {
		if (!this.elements.otp) {
			return;
		}
		this.elements.otp.style.marginTop =
			document.querySelector('#content p').offsetTop - document.querySelector('#content').offsetTop + 'px';
		if (isFirstLoad) {
			this.elements.otp.classList.add('show'); // NOTE: this is just an example of how it might be done.
		}
	}

	/**
	 * @param {string} element global element to be retrieved
	 * @returns HTML Element
	 */
	getElement(element) {
		let { [element]: htmlElement } = this.elements || null;
		return htmlElement;
	}

	/**
	 * General place for debugging logic
	 * @TODO Determine what is appropriate for different environments with instructions for enabling if
	 */
	debug() {
		console.debug(arguments);
	}
}

// there can only be 1
if (!window.CDC || !CDC.Page) {
	CDC.Page = new CDCPage();
}
