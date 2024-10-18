const express = require("express")
const ipp = require("ipp");
const printer = ipp.Printer("ipp://CP1500ecdf2f.local:631/ipp/print");
const fs = require("fs");

const PORT = 5050;
const IMAGE_DIRECTORY = "/home/photobooth/boxcom/images";

const app = express();
app.use(express.json());

var paperStock = 18;
var printCount = 0;


app.get("/printer/is_ready", (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: GET /printer/is_ready");
});


app.post("/printer/order", async (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: POST /printer/order");

    console.log("Printing image " + req.body.image_id);

    var document;

    let image_id = req.body.image_id;

    console.log("Reading file: " + IMAGE_DIRECTORY + "/img" + image_id + ".jpg")
    fs.readFile(IMAGE_DIRECTORY + "/img" + image_id + ".jpg", function (err, data) {
        if (err) {
            throw err;
        }

        document = data;
    });

    var msg = {
        "operation-attributes-tag": {
            "requesting-user-name": "Fotobox",
            "document-format": "image/jpeg"
        },
        data: document
    };

    printer.execute("Print-Job", msg, function (err, res) {
        console.log("[PRINTER]");
        console.log("\tERROR");
        console.log(err);
        console.log("\tRESULT");
        console.log(res);
    });

    printCount++;

    res.status(200).send("OK");
});


app.get("/printer/stock", (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: GET /printer/stock");
    res.status(200).send({ stock: paperStock });
});

app.post("/printer/stock", (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: POST /printer/stock");
    if (req.body.stock == undefined) {
        res.status(400).send("Stock cannot be undefined");
        return;
    }
    paperStock = req.body.stock;
    console.log("New stock: " + paperStock);
    res.status(200).send("OK");
});


app.get("/printer/print_count", (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: GET /printer/print_count");
    res.status(200).send({ count: printCount })
});


app.listen(PORT, () => {
    console.log(`Printer interface listening on port ${PORT}`)
})
