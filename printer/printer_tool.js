var ipp = require("ipp");
var printer = ipp.Printer("ipp://CP1500ecdf2f.local:631/ipp/print");

var msg = {
  "operation-attributes-tag": {
    "requesting-user-name": "John Doe",
    "document-format": "image/pwg-raster",
    "requested-attributes": ["printer-description", "job-template", "media-col-database"]
  }
};

printer.execute("Get-Printer-Attributes", msg, function(err, res) {
        console.log(err);
        console.log(res);
});
