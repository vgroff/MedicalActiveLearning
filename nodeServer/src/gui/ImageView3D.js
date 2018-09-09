import React, { Component } from 'react'
import {ImageView2D} from "./ImageView2D.js"

// Container holding 3 2D Image containers
export class ImageView3D extends Component {

    constructor(props) {
	super(props)
	this.props = props
	this.state = {}
    }

    drawAll() {
	this.refs.imgX.drawImage()
	this.refs.imgY.drawImage()
	this.refs.imgZ.drawImage()
    }

    resetImageIndices() {
	this.refs.imgX.setImageIndex(0)
	this.refs.imgY.setImageIndex(0)
	this.refs.imgZ.setImageIndex(0)
    }

    preRender() {
	this.refs.imgX.preRenderImages()
	this.refs.imgY.preRenderImages()
	this.refs.imgZ.preRenderImages()
    }

    render() {
	if (this.props.image) {
	    console.log("Drawing 3d")
	    var axes = [ ["imgX", this.props.image.imagesX],
			 ["imgY", this.props.image.imagesY],
			 ["imgZ", this.props.image.imagesZ] ]
	    return (
		<div>

		{axes.map( function(ax, index) {
		    return (
			<ImageView2D ref={ax[0]} key={index} images = {ax[1]}
			maskVisibility = {this.props.maskVisibility}
			level = {this.props.level} window = {this.props.window}
			brushSize={this.props.brushSize} 
			maskColours = {this.props.maskColours} maskLabel={this.props.maskLabel}
			action={this.props.action} onChange={this.drawAll.bind(this)}/>
		    )
		}.bind(this))}
		

		</div>
	    )
	}
	else {
	    return (<div></div>)
	}
    }
}
