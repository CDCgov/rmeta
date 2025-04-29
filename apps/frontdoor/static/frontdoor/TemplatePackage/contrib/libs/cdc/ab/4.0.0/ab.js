'use strict';

( function( window ) {

	if ( 'undefined' !== typeof CDC && 'undefined' !== typeof CDC.ABTest ) {

		var now = new Date();

		var testId = CDC.ABTest.id();
		var testType = CDC.ABTest.type();
		var redirect = CDC.ABTest.redirect();
		var testActive = CDC.ABTest.active();
		var testViewports = CDC.ABTest.viewports();
		var callback = CDC.ABTest.callback();
		var defaultReportSuite = s ? s.account : 'devcdc';
		var apiEndpoint = 'https://tools.cdc.gov/abtest/variant/seed?c=2&ex=';

		var abId;
		var reportSuite;
		var useVariant;
		var abCookieValue;
		var abCookie;
		var abCookies;
		var cookies;

		var queryParms = window.location.href.slice( window.location.href.indexOf( '?' ) + 1 ).split( '&' );

		var highlightParam = $.grep( queryParms, function( param ) {
			return -1 < param.indexOf( 'highlight=true' );
		} );
		var highlight = 0 < highlightParam.length;

		var overrideVariant = $.map( queryParms, function( param ) {
			if ( -1 < param.indexOf( 'variant=' ) ) {
				return param.split( '=' )[ 1 ];
			} else {
				return null;
			}
		} );

		var expDate = new Date();
		expDate.setTime( expDate.getTime() + ( 356 * 24 * 60 * 60 * 1000 ) ); // add 1 year

		//
		// Method to run A/B redirect test.
		//
		var runRedirectTest = function() {
			// Use the values passed in on the redirect object within the settings to determine whether to redirect or not and to send metrics.
			abId = redirect.id;
			var percent = redirect.percent;

			abId = 'AB_Redirect_' + abId;

			// Check to see if report suite has been overridden.
			reportSuite = redirect.reportSuite;
			if ( 'undefined' === typeof reportSuite || 0 === reportSuite.length ) {
				reportSuite = defaultReportSuite;
			}

			useVariant = Math.floor( Math.random() * 100 ) + 1 > ( 100 - percent );
			var currentUrl = window.location.href;
			var baselineUrl = redirect.baselineUrl;
			var variantUrl = redirect.variantUrl;

			// Check to see if variant page is being directly hit via bookmark/direct link.
			if ( currentUrl === variantUrl && '' === document.referrer ) {
				// We are on the variant page, but got here directly.  Go back to baseline page to run the A/B test.
				window.location = baselineUrl;
			} else if ( currentUrl === baselineUrl || currentUrl === variantUrl ) {
				// We are on a page that is part of this split page/redirect test.
				abCookieValue = '';
				abCookie = '';
				abCookies = [];
				if ( redirect.sticky ) {
					cookies = document.cookie.split( ';' );
					abCookies = cookies.filter( function( cookieItem ) {
						return -1 < cookieItem.indexOf( 'CDC_ABTest_Redirect_' + testId + '_' + redirect.id );
					} );
					if ( 0 < abCookies.length ) {
						abCookie = abCookies[ 0 ].split( '=' );
						if ( 0 < abCookie.length ) {
							abCookieValue = abCookie[ 1 ];
							useVariant = abCookieValue === variantUrl ? true : abCookieValue === baselineUrl;
						}
					}
				}

				if ( currentUrl === variantUrl && '' === abCookieValue && redirect.sticky ) {
					// We are on the variant page, but got here without a cookie being set by the baseline page.  Go back to baseline page to run the A/B test.
					useVariant = false;
					window.location = baselineUrl;
				} else if ( currentUrl === abCookieValue || '' === abCookieValue ) {
					var abOption = currentUrl === variantUrl ? 'variant' : 'baseline';
					var targetUrl = useVariant ? variantUrl : baselineUrl;

					s.prop64 = testId;
					s.eVar8 = abOption;

					document.cookie = 'CDC_ABTest_Redirect_' + testId + '_' + redirect.id + '=' + targetUrl + '; path=/; secure';
				} else {
					useVariant = false;
				}

			} else {
				useVariant = false;
			}

			if ( useVariant && ( window.location.href !== targetUrl ) ) {
				s = {};
				ga = {};
				window.location = targetUrl;
			} else {
				document.documentElement.className = document.documentElement.className.replace( RegExp( ' ?d-none' ), '' );
			}

			// Rewrite the URL in the left nav if we are on the variant page.
			if ( window.location.href.toLowerCase() !== baselineUrl.toLowerCase() ) {
				var baselineRelUrl = baselineUrl;
				if ( -1 < baselineRelUrl.indexOf( '//' ) ) {
					baselineRelUrl = baselineRelUrl.substring( baselineRelUrl.indexOf( '//' ) + 2 );
					baselineRelUrl = baselineRelUrl.substring( baselineRelUrl.indexOf( '/' ) );
				}

				var currentRelUrl = window.location.href;
				if ( -1 < currentRelUrl.indexOf( '//' ) ) {
					currentRelUrl = currentRelUrl.substring( currentRelUrl.indexOf( '//' ) + 2 );
					currentRelUrl = currentRelUrl.substring( currentRelUrl.indexOf( '/' ) );
				}

				if ( 0 < $( 'nav ul li a[href="' + baselineRelUrl + '"]' ).length ) {
					$( 'nav ul li a[href="' + baselineRelUrl + '"]' ).attr( 'href', currentRelUrl );
				}
			}
		}

		//
		// Method to run A/B module test.
		//
		var runModuleTest = function() {

			// The master deferred.
			var dfd = $.Deferred();
			var dfdNext = dfd; // Next deferred in the chain
			var values = [];

			var modules = $( 'div[data-abid]' );
			var count = modules.length;

			var callApi = function( value ) {
				var dfdAjax = $.Deferred();

				var experimentId;
				if ( 1 < count ) {
					experimentId = testId + '-' + value;
				} else {
					experimentId = testId;
				}

				// Get sample/switch percentage (default is 50).
				var requestedPercentAttr = item.attr( 'data-percent-variant' );
				var requestedPercent = 50;
				if ( requestedPercentAttr && !isNaN( parseInt( requestedPercentAttr ) ) ) {
					requestedPercent = parseInt( requestedPercentAttr );
				}

				// Determine if the showing of baseline versus variant is being persisted in a cookie (i.e., is "sticky").
				var requestedStickiness = item.attr( 'data-sticky' );
				var stickiness = 'true';
				if ( requestedStickiness && 0 < requestedStickiness.length ) {
					stickiness = requestedStickiness;
				}

				abCookieValue = '';
				abCookie = '';
				abCookies = [];

				// Get the value stored in the cookie for this module/experiment if we are persisting this (if any value has been set).
				if ( 'true' === stickiness || stickiness ) {
					cookies = document.cookie.split( ';' );
					abCookies = cookies.filter( function( cookieItem ) {
						return -1 < cookieItem.indexOf( 'CDC_ABTest_' + testId + '_' + value );
					} );

					if ( 0 < abCookies.length ) {
						abCookie = abCookies[ 0 ].split( '=' );
						if ( 0 < abCookie.length ) {
							abCookieValue = abCookie[ 1 ];
						}
					}
					console.log( 'cookie key', 'CDC_ABTest_' + testId + '_' + value );
					console.log( 'abCookieValue', abCookieValue );

				}

				if ( '' !== abCookieValue && ( stickiness || 'true' === stickiness ) ) {
					item.attr( 'data-abid', abId );
					item.attr( 'data-ab-show', abCookieValue );
					dfdAjax.resolve( abCookieValue );
				} else if ( '' === abCookieValue ) {
					// We don't have a cookie value so we need to hit the API to figure out whether to serve up the baseline or variant.
					$.ajax( {
						url: apiEndpoint + experimentId + '&s=' + requestedPercent,
						success: function( result ) {
							var item = $( 'div[data-abid="' + value + '"]' );
							if ( 1 === JSON.parse( result ).variant ) {
								$( item ).attr( 'data-ab-show', 'variant' );
							} else {
								$( item ).attr( 'data-ab-show', 'baseline' );
							}
							dfdAjax.resolve( JSON.parse( result ).variant );
						}
					} );
				}

				return dfdAjax.promise();
			};

			// This would be a user function that makes an ajax request.
			// In normal code you'd be using $.ajax instead of simulateAjax.
			var requestAjax = function( value ) {
				return callApi( value );
			};

			// Deferred pipe chaining.
			// What you want to note here is that an new
			// ajax call will not start until the previous
			// ajax call is completely finished.
			for ( var x = 0; x < count; x++ ) {

				var item = $( modules[ x ] );
				values.push( item.attr( 'data-abid' ) );

				dfdNext = dfdNext.pipe( function() {
					var value = values.shift();
					return requestAjax( value ).
						done( function( response ) {
							// Process the response here if needed.
						} );
				} );

			}
			dfdNext = dfdNext.pipe( function() {
				var cdcAbDivs = $( 'div[data-abid]' );
				$.each( cdcAbDivs, function( index, elem ) {

					var cdcAbDiv = $( elem );
					if ( overrideVariant && 0 < overrideVariant.length ) {
						var overrides = overrideVariant[ 0 ].split( ',' );
						var override = 'false';
						if ( index < overrides.length ) {
							override = overrides[ index ];
						}
						if ( 'true' === override ) {
							cdcAbDiv.attr( 'data-ab-show', 'variant' );
						} else {
							cdcAbDiv.attr( 'data-ab-show', 'baseline' );
						}
					}

					var variantContentId = cdcAbDiv.attr( 'id' );
					var selector = cdcAbDiv.attr( 'data-selector' );
					if ( 'variant' === cdcAbDiv.attr( 'data-ab-show' ) ) {
						var block = $( '#' + variantContentId ).contents();
						var repl = $( '<div />' );
						for ( var i = 0; i < block.length; i++ ) {
							if ( 8 === block[ i ].nodeType ) {
								repl = $( block[ i ].nodeValue );
								break;
							}
						}
						repl.attr( 'id', variantContentId );
						repl.attr( 'data-ab-show', 'variant' );
						repl.attr( 'data-abid', cdcAbDiv.attr( 'data-abid' ) );
						repl.attr( 'data-selector', '#' + variantContentId );
						var externalLinks = [];
						$( selector ).find( 'a[class*="tp-link-policy"]' ).each( function( anchorIndex, anchorElem ) {
							externalLinks.push( $( anchorElem ).attr( 'href' ) );
						} );
						// Remove the element that had the variant markup used to construct the new variant element.
						$( '#' + variantContentId ).remove();
						// Replace the baseline markup with the new variant element.
						$( selector ).replaceWith( repl );
						for ( var externalLinksIndex = 0; externalLinksIndex < externalLinks.length; externalLinksIndex++ ) {
							$( repl ).find( 'a[href="' + externalLinks[ externalLinksIndex ] + '"]' ).addClass( 'tp-link-policy' )
								.append( $( '<span class="sr-only">external icon</span><span class="fi cdc-icon-external x16 fill-external" aria-hidden="true"></span>' ) );
						}
						// Set the selector to be the ID reference to the now displayed variant element (only used in highlighting logic below).
						selector = '#' + variantContentId;
						// Set the cookie.
						document.cookie = 'CDC_ABTest_' + testId + '_' + cdcAbDiv.attr( 'data-abid' ) + '=variant; expires=' + expDate.toGMTString() + '; path=/; secure';
					} else {
						$( selector ).attr( 'data-abid', cdcAbDiv.attr( 'data-abid' ) );
						$( selector ).attr( 'data-ab-show', 'baseline' );
						document.cookie = 'CDC_ABTest_' + testId + '_' + cdcAbDiv.attr( 'data-abid' ) + '=baseline; expires=' + expDate.toGMTString() + '; path=/; secure';
						cdcAbDiv.remove();
					}

					if ( highlight ) {
						$( '*[data-abid]' ).attr( 'style', 'border: 4px solid rgb(201, 34, 34)!important; padding: 4px!important' );
					}
				} );

				// Fire the page view when Adobe Launch is loaded/available
				var attempts = 0;
				var interval = setInterval( function() {

					var root = document.getElementsByTagName( 'body' )[ 0 ];
					if ( 0 > root.className.indexOf( 'adobe-launch-complete' ) ) {
						attempts++;
					} else {
						clearInterval( interval );

						// Set the click handlers for the module(s) in the A/B test
						$( '[data-abid]' ).each( function( divIndex, divElem ) {
							var parentAbDiv = $( divElem );
							var anchorCount = 0;
							var abAnchorCount = 0;
							var anchors = [];
							if ( parentAbDiv.is( 'a' ) ) {
								anchors.push( parentAbDiv );
								anchorCount = 1;
								abAnchorCount = 0;
							} else {
								anchorCount = $( parentAbDiv ).find( 'a' ).length;
								abAnchorCount = $( parentAbDiv ).find( 'a.ab-track-link' ).length;
								anchors = parentAbDiv.find( 'a' );
							}
							$( anchors ).each( function( anchorIndex, elem ) {
								var abAnchor = $( elem );
								if ( ! abAnchor.hasClass( 'tp-link-policy' ) ) {
									abAnchor.on( 'click', function( e ) {
										e.stopImmediatePropagation();
										e.preventDefault();
										var tag = $( this );
										var trackLink = false;
										if ( ( 1 < anchorCount && 0 === abAnchorCount ) || ( 1 === anchorCount && 0 === abAnchorCount ) ) {
											trackLink = true;
										} else if ( tag.is( 'a' ) ) {
											trackLink = tag.hasClass( 'ab-track-link' );
										} else if ( 1 === tag.children( 'a' ).length ) {
											trackLink = tag.children( 'a' ).hasClass( 'ab-track-link' );
										}
										if ( trackLink ) {
											s.pageName = null;
											s.prop64 = testId;
											s.events = 'event2';
											s.eVar8 = parentAbDiv.attr( 'data-abid' ) + '_' + parentAbDiv.attr( 'data-ab-show' );
											s.linkTrackEvents = 'event2';
											s.linkTrackVars = 'prop2,prop31,prop46,prop18,prop64,pageName,event2,eVar8';
											s.tl( true, 'o', tag.attr( 'href' ) );
										}
										if ( tag.is( 'a' ) ) {
											setTimeout( function( url ) {
												window.location = url;
											}, 200, tag.attr( 'href' ) );
										} else if ( 1 === tag.children( 'a' ).length ) {
											setTimeout( function( url ) {
												window.location = url;
											}, 200, tag.children( 'a' ).attr( 'href' ) );
										}
										return false;
									} );
								}
							} );
						} );

						s.prop64 = testId;
						s.eVar8 = cdcAbDivs.map( function() {
							abId = $( this ).attr( 'data-abid' );
							var abOption = $( this ).attr( 'data-ab-show' );
							var id = $( this ).attr( 'id' );
							if ( 'undefined' === typeof abOption || '' === abOption ) {
								if ( 'undefined' === typeof id || '' === id ) {
									abOption = 'not_set';
								} else {
									abOption = 'baseline';
								}
							}
							return abId + '_' + abOption;
						} ).get().join( ';' );

						s.t();
					}
					if ( 20 < attempts ) {
						clearInterval( interval );
						console.log( 'Adobe Launch failed to load after 20 attempts' );
					}

				}, 500 );

				document.documentElement.className = document.documentElement.className.replace( RegExp( ' ?d-none' ), '' );

				return callback();
			} );

			// Start the pipe chain.
			dfd.resolve();

		};

		var findTp4Viewport = function() {
			var result = '';
			var envs = [ 'xs', 'sm', 'md', 'lg', 'xl', 'xxl' ];
			var el = $( '<div />' );
			el.appendTo( $( 'body' ) );
			for ( var i = envs.length - 1; 0 <= i; i-- ) {
				var env = envs[ i ];
				el.addClass( 'd-' + env + '-none' );
				if ( 'none' === el.css( 'display' ) ) {
					el.remove();
					result = env;
					break;
				}
			}
			return result;
		};

		//
		// Check to see if the test is restricted to certain viewports and, if so, check to see if the current viewport is in the ones specified for the test.
		//
		var currentViewport = findTp4Viewport();
		if ( testActive ) {
			if ( testViewports && 0 < testViewports.length && '' !== currentViewport ) {
				testActive = -1 < $.inArray( currentViewport, testViewports );
			}
		}

		//
		// Check to see what type of test is being requested and run the test(s).
		//
		if ( testActive ) {
			if ( CDC.ABTest.TEST_TYPE_REDIRECT === testType ) {
				runRedirectTest();
			} else {
				runModuleTest();
			}
		} else {
			// No active test.  Just re-enable the page display.
			document.documentElement.className = document.documentElement.className.replace( RegExp( ' ?d-none' ), '' );
		}

	}

} )( window );
