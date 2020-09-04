<template>
<div>
  <file-upload
    ref="upload"
    v-model="files"
    :multiple="true"
    :drop="true"
    :drop-directory="false"
    post-action="/post.method"
    put-action="/put.method"
    @input-file="inputFile"
    @input-filter="inputFilter"
  >
  Drag and Drop the PDF document or JPG pages here or click here to Browse for files.
  </file-upload>

    <div v-for="(file, index) in files" v-bind:key="index">
      <img v-if="file.blob" :src="file.blob" width="80" height="auto" />
      {{file.name}} - {{ Math.round(file.size/1024 * 100) / 100 }} KB
      <button type="button" @click.prevent="$refs.upload.remove(file)">Remove</button>
      <button type="button" @click.prevent="moveUp(index)" style="z-index: 999" :disabled="index === 0">up</button>
      <button type="button" @click.prevent="moveDown(index)" :disabled="index >= (files.length - 1)">down</button>
    </div>

</div>
</template>

<script>
import VueUploadComponent from 'vue-upload-component'

export default {
  data: function () {
    return {
      files: []
    }
  },
  components: {
    FileUpload: VueUploadComponent
  },
  methods: {
    /**
     * Has changed
     * @param  Object|undefined   newFile   Read only
     * @param  Object|undefined   oldFile   Read only
     * @return undefined
     */
    inputFile(newFile, oldFile) {
      if (newFile && oldFile && !newFile.active && oldFile.active) {
        // Get response data
        console.log('response', newFile.response)
        if (newFile.xhr) {
          //  Get the response status code
          console.log('status', newFile.xhr.status)
        }
      }
    },
    /**
     * Pretreatment
     * @param  Object|undefined   newFile   Read and write
     * @param  Object|undefined   oldFile   Read only
     * @param  Function           prevent   Prevent changing
     * @return undefined
     */
    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        // Filter non-image file
        if (!/\.(jpeg|jpg|png|pdf)$/i.test(newFile.name)) {
          return prevent()
        }
      }

      // Create a blob field
      newFile.blob = ''
      let URL = window.URL || window.webkitURL
      if (URL && URL.createObjectURL) {
        newFile.blob = URL.createObjectURL(newFile.file)
      }
    },
    moveUp(old_index) {
      if (old_index >= 1 && this.files.length > 1) {
        this.files.splice(old_index - 1, 0, this.files.splice(old_index, 1)[0]);
      }
    },
    moveDown(old_index) {
      if (old_index <= this.files.length && this.files.length > 1) {
        this.files.splice(old_index + 1, 0, this.files.splice(old_index, 1)[0]);
      }
    }    
  }
}
</script>

<style scoped lang="scss">
  span.file-uploads {
    width: 100%;
    display: flex;
    flex-direction: column;
    min-height: 60px;
    align-items: center;
    justify-content: center;
    border: 1px #000 dashed;
    border-radius: 6px;

    &:hover {
      background-color: #eee;
    }
  }
</style>
