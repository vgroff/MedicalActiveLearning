import React, { Component } from 'react'
var nifti = require('nifti-reader-js')

function readNifti(file) {
    //var buf = fs.readFileSync(filename);
    //var data = nifti.Utils.toArrayBuffer(buf);
    var fr = new FileReader()
    var data = fr.readAsArrayBuffer(file)
    fr.onloadend = function(evt) { console.log(data) }
    var niftiHeader = null,
	niftiImage = null,
	niftiExt = null;
    if (nifti.isCompressed(data)) {
	data = nifti.decompress(data);
    }
    if (nifti.isNIFTI(data)) {
	niftiHeader = nifti.readHeader(data);
	console.log(niftiHeader.toFormattedString());
	niftiImage = nifti.readImage(niftiHeader, data);
	
	if (nifti.hasExtension(niftiHeader)) {
	    niftiExt = nifti.readExtensionData(niftiHeader, data);
	}
	return niftiImage
    }
    return null
}

class App extends Component {
    constructor(props) {
	super(props)
	this.state = {currentImage: null}
	//readNifti("./T1.nii.gz")
    }
    readNewImage(data) {
	console.log(data)
	var niftiHeader = null,
	    niftiImage = null,
	    niftiExt = null;
	if (nifti.isCompressed(data)) {
	    data = nifti.decompress(data);
	}
	if (nifti.isNIFTI(data)) {
	    niftiHeader = nifti.readHeader(data);
	    console.log(niftiHeader.toFormattedString());
	    niftiImage = nifti.readImage(niftiHeader, data);
	    
	    if (nifti.hasExtension(niftiHeader)) {
		niftiExt = nifti.readExtensionData(niftiHeader, data);
	    }
	    console.log("image Parsed")
	    this.currentImage = niftiImage
	    console.log(this.currentImage, niftiHeader)
	}
    }
    changeImage(file) {
	//var buf = fs.readFileSync(filename);
	//var data = nifti.Utils.toArrayBuffer(buf);
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
                this.readNewImage(evt.target.result)
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }
    render() {
	return (<div>
		<p>Hello</p>
		<p>Select a file: <input onChange={(e) => {this.changeImage(e.target.files[0])}} type="file" id="file" name="files" /></p>
		</div>
	       )
    }
}
export default App
