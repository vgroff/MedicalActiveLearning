import React, { Component } from 'react'

import {ImageView} from "./ImageView.js"
import {convertNifti} from "./utils/nifti.js"


class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imagesX: {}, imagesY: {}, imagesZ: {}}
    }

    changeImage(file) {
	console.log("img changed")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    console.log("img loaded")
	    if (evt.target.readyState === FileReader.DONE) {
                var imgs = convertNifti(evt.target.result)
		console.log("img converted")
		this.setState({imagesX : imgs[0], imagesY : imgs[1], imagesZ : imgs[2]})
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }
    
    readNewImages(data) {

    } 
    
    render() {
	return (<div>
		<p>Hello</p>
		<p>Select a file: <input onChange={(e) => {this.changeImage(e.target.files[0])}} type="file" id="file" name="files" /></p>
		<ImageView images = {this.state.imagesX}/>
		<ImageView images = {this.state.imagesY}/>
		<ImageView images = {this.state.imagesZ}/>
		</div>
	       )
    }
}
export default App

/*
 * Order:
 * - Display all 3
 * - Consider how to deal with scaling issues - we have voxel dims that we can normalize to 1, and maybe what we return is an array of objects for each x,y,z with imgDat and pixel height/width
 * - Having image scrolling
 * TO-DO:
 * - Need a transfer function for mapping the 16bit values to whatever range needed, since they are too low to express in raw 16-bit and this is generally how it is done
 * - Need to scroll through several images
 * - Pixel sizes matter
*/
