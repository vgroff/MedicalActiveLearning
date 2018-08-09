var nifti = require('nifti-reader-js')
import {Image} from "./image.js"
import {Image3D} from "./image3d.js"

export function getImageData(data,  norm) {
    var niftiHeader = null,
	niftiImage = null,
	niftiExt = null;
    // Decompress if needed
    if (nifti.isCompressed(data)) {
	data = nifti.decompress(data);
    }
    // If valid NIFTI data
    if (nifti.isNIFTI(data)) {
	// Separate image and header data
	niftiHeader = nifti.readHeader(data);
	console.log("header", niftiHeader)
	niftiImage = nifti.readImage(niftiHeader, data);
	// Get the dimensions
	var height = niftiHeader.dims[2]
	var width = niftiHeader.dims[1]
	var depth = niftiHeader.dims[3]
	if (nifti.hasExtension(niftiHeader)) {
	    niftiExt = nifti.readExtensionData(niftiHeader, data);
	}
	// Depending on the bitdepth, convert the current image to an array
	var image
	var maxVal
	if (niftiHeader.numBitsPerVoxel == 8) {
	    image = new Uint8Array(niftiImage)
	    maxVal = 2**8 - 1
	}
	else if (niftiHeader.numBitsPerVoxel == 16) {
	    image = new Uint16Array(niftiImage)
	    maxVal = 2**16 - 1
	}
	else if (niftiHeader.numBitsPerVoxel == 32 && niftiHeader.datatypeCode === 8) {
	    image = new Int32Array(niftiImage)
	    maxVal = 2**32 - 1
	}
	else if (niftiHeader.numBitsPerVoxel == 32 && niftiHeader.datatypeCode === 16) {
	    image = new Float32Array(niftiImage)
	    maxVal = 2**32 - 1
	}
	else if (niftiHeader.numBitsPerVoxel == 64 && niftiHeader.datatypeCode === 1024) {
	    image = new Int64Array(niftiImage)
	    maxVal = 2**64 - 1
	}
	else {
	    console.log("Error, unrecognized bit depth in image")
	    alert("Error, unrecognized bit depth in image")
	    return
	}
	console.log(niftiHeader)
	var max = 0
	for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
	    // Iterate over the number of expected images (3rd dimension)
	    var imgStart = height*width*imgN 
	    // Copy the array over to a 2-d array 
	    for (var y = 0; y < height; y++) {
		for (var x = 0; x < width; x++) {
		    var idx = (imgStart + width * y + x);
		    if (max < image[idx]) {
			max = image[idx]
		    }
		}
	    }
	}
	var dataX = []
	var mean = 0
	var stdDev = 0
	var counts = 0
	for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
	    // Iterate over the number of expected images (3rd dimension)
	    dataX.push([])
	    var imgStart = height*width*imgN 
	    // Copy the array over to a 2-d array 
	    for (var y = 0; y < height; y++) {
		dataX[imgN].push([])
		for (var x = 0; x < width; x++) {
		    var idx = (imgStart + width * y + x);
		    var val = image[idx]
		    if (norm === true) {
			val = val/max
		    }
		    dataX[imgN][y].push(val)
		    if (image[idx] / max > 0.01) {
			mean += val
			counts += 1
		    }
		}
	    }
	}
	console.log("MEAN", mean/(counts), dataX)
	let pixDims = niftiHeader.pixDims
	return [dataX, pixDims[2], pixDims[1], pixDims[3], mean/counts, max]
    }
    else {
	alert("File not recognised")
	return false
    }
}

// Take NIFTI file data and return the grayscale image values
export function convertNifti(data, norm) {
    var res = getImageData(data, norm)
    var dataX = res[0]
    var image3D = new Image3D(dataX, res[1], res[2], res[3])
    return [image3D, res[4], res[5]]
}
