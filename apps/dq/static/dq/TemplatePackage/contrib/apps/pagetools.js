/**
 * @version 4.24.10
 * Date: 2024-12-03T08:06:03.012Z
 */
/**
 * Loads Page Info tab and contacts on page
 * @param {boolean} unblock Override block queryparam
 */
$(() => {
	if (document.body.classList.contains('cdc-page-tools')) {
		return;
	}
	const hostname = String(document.location.hostname).toLowerCase();

	// start false
	let loadPageTools = false;

	// localhost always loads tools
	const allowedHostnames = 'localhost|vvvdev.wcms'.split('|');
	if (allowedHostnames.includes(hostname)) {
		loadPageTools = true;
	}

	// cdc.gov domains must be checked
	if (hostname.includes('.cdc.gov')) {
		const subDomain = hostname.replace('.cdc.gov', '');
		const allowedSubDomains = ('wwwdev|betadev|emergencydev|emergencytest|atsdrdev|atsdrtest|intradev|' +
			'intratest|intrauat|traveldev|traveltest|opendev|coviddev|covidtest|millionhearts-dev|' +
			'test.open|wwwncdev|wwwnctest|wwwndev|wwwntest|nccddev|nccdintra|prototypedev|prototypetest|' +
			'oadc-dmb-dev|oadc-dmb-test|oadc-dmb-stage|aidv-cshs-dev1').split('|');
		allowedSubDomains.forEach(snippet => {
			loadPageTools = loadPageTools || subDomain.includes(snippet.trim());
		})
	}

	// allow query params to disable loading
	if (loadPageTools) {

		// ?tools=n disables display of page tools
		loadPageTools = CDC.Common.getParamSwitch('tools', true);

		// page variables can disable
		if ( false === window.PIT ) {
			loadPageTools = false;
		}
		if ( false === window.CDC_TOOLS ) {
			loadPageTools = false;
		}
	}

	// finally if load page tools, do so
	if (loadPageTools) {

		$('body:first').append('<div id="pit-dashboard"></div>');
		CDC.Common.loadCss('/TemplatePackage/contrib/apps/pageinfo/main.css');
		CDC.Common.loadJS('/TemplatePackage/contrib/apps/pageinfo/main.js');

		// add body class to note tools are loaded
		document.body.classList.add('cdc-page-tools')
	}
});
