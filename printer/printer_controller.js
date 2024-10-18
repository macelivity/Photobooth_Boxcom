const express = require("express")
const ipp = require("ipp");
const Printer = ipp.Printer("http://printer.example.com:631/ipp/print");
const fs = require("fs");
const saver = require("file-saver");

const PORT = 5050;
const WEBISTE_URL = "http://localhost:8447";
const IMAGE_DIRECTORY = "";

const app = express();
app.use(express.json());

var paperStock = 18;
var printCount = 0;

var auth = "unauthorized";

function authorize() {
    fetch(WEBISTE_URL + "/api/login/printer", {
        method: "POST",
        body: "Paul+Leonie=<3"
    })
        .then(async res => {
            auth = await res.text();
            console.log(auth);
        });
}

authorize();


app.get("/printer/is_ready", (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: GET /printer/is_ready");
});


app.post("/printer/order", async (req, res) => {
    console.log("[" + new Date().toLocaleString() + "] <" + req.hostname + ">: POST /printer/order");

    res.status(200).send("OK");
    console.log(req.body);
    console.log(WEBISTE_URL + "/api/images/" + req.body.url);
    let fetchImageResponse = await fetch(WEBISTE_URL + "/api/images/" + req.body.url, {
        headers: {
            'Cookie': "auth=" + auth
        }
    });
    const image = await fetchImageResponse.blob();
    saver.saveAs(image, "MyBlob.jpg");
    console.log("Saved file");
    return;

    var document;

    let image_id = req.body;

    fs.readFile(IMAGE_DIRECTORY + "/" + image_id, function (err, data) {
        if (err) throw err;

        document = data;
    });

    var msg = {
        "operation-attributes-tag": {
            "requesting-user-name": "Fotobox",
            "document-format": "image/jpg"
        },
        data: document
    };

    printer.execute("Print-Job", msg, function (err, res) {
        console.log(err);
        console.log(res);
    });

    printCount++;
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
    console.log(`Example app listening on port ${PORT}`)
})
