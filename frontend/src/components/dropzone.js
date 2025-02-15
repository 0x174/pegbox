import React, {useCallback} from 'react'
import {useDropzone} from 'react-dropzone'

class UCFFile {
  constructor(height, width) {
    this.height = height;
    this.width = width;
  }
}

function UCFDropzone() {
 const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach((file) => {
      const reader = new FileReader()

      reader.onabort = () => console.log('file reading was aborted')
      reader.onerror = () => console.log('file reading has failed')
      reader.onload = () => {
      // Do whatever you want with the file contents
        const binaryStr = reader.result
        console.log(binaryStr)
        let json = JSON.parse(binaryStr)
        console.log(json)
        console.log(json )
      }
      reader.readAsText(file)
    })

  }, [])
  const {getRootProps, getInputProps} = useDropzone({onDrop})

  return (
    <div {...getRootProps()}>
      <input {...getInputProps()} />
      <p>Drag 'n' drop some files here, or click to select files</p>
    </div>
  )
}

export default UCFDropzone;