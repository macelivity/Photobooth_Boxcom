var mdns = require('mdns'),
	browser  = mdns.createBrowser(mdns.tcp('ipp'));
	
mdns.Browser.defaultResolverSequence[1] = 'DNSServiceGetAddrInfo' in mdns.dns_sd ? mdns.rst.DNSServiceGetAddrInfo() : mdns.rst.getaddrinfo({families:[4]}); 

browser.on('serviceUp', function (rec) {
	console.log(rec.name, 'http://'+rec.host+':'+rec.port+'/'+rec.txtRecord.rp);
});
browser.start();