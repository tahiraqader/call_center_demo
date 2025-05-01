
// // import { Component } from '@angular/core';
// // import { RestService } from '../services/rest-service.service';

// // @Component({
// //   selector: 'app-file-upload',
// //   templateUrl: './file-upload.component.html',
// //   styleUrls: ['./file-upload.component.scss']
// // })
// // export class FileUploadComponent {
// //   selectedFile: File | null = null;
// //   isUploading = false;

// //   constructor(private restService: RestService) {}

// //   onFileSelected(event: any): void {
// //     this.selectedFile = event.target.files[0];
// //   }

// //   uploadFile(): void {
// //     if (!this.selectedFile) return;

// //     this.isUploading = true;

// //     const formData = new FormData();
// //     formData.append('file', this.selectedFile);

// //     this.restService.uploadFile(this.selectedFile).subscribe({
// //       next: (response) => {
// //         console.log('Upload success:', response);
// //       },
// //       error: (error) => {
// //         console.error('Upload error:', error);
// //       },
// //       complete: () => {
// //         this.isUploading = false;
// //         this.selectedFile = null;
// //       }
// //     });
// //   }
// // }
// import { Component } from '@angular/core';
// import { RestService } from '../services/rest-service.service';

// @Component({
//   selector: 'app-file-upload',
//   templateUrl: './file-upload.component.html',
//   styleUrls: ['./file-upload.component.scss']
// })
// export class FileUploadComponent {
//   selectedFile: File | null = null;
//   isUploading = false;
//   audioPreviewUrl: string | null = null;

//   constructor(private restService: RestService) {}

//   onFileSelected(event: any): void {
//     this.selectedFile = event.target.files[0];
//     if (this.selectedFile) {
//       this.audioPreviewUrl = URL.createObjectURL(this.selectedFile);
//     } else {
//       this.audioPreviewUrl = null;
//     }
//   }

//   uploadFile(): void {
//     if (!this.selectedFile) return;

//     this.isUploading = true;

//     const formData = new FormData();
//     formData.append('file', this.selectedFile);

//     this.restService.uploadFile(this.selectedFile).subscribe({
//       next: (response) => {
//         console.log('Upload success:', response);
//       },
//       error: (error) => {
//         console.error('Upload error:', error);
//       },
//       complete: () => {
//         this.isUploading = false;
//         this.selectedFile = null;
//         this.audioPreviewUrl = null;
//       }
//     });
//   }
// }
import { Component } from '@angular/core';
import { RestService } from '../services/rest-service.service';


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  selectedFile: File | null = null;
  audioPreviewUrl: string | null = null;
  isUploading = false;
  previewVisible: boolean = false;
  hasUploaded: boolean = false;

  constructor(private restService: RestService) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
    this.previewVisible = false;
    this.audioPreviewUrl = null;
    this.hasUploaded = false;
  }
  previewAudio(): void {
    if (!this.selectedFile) return;
  
    const reader = new FileReader();
    reader.onload = () => {
      this.audioPreviewUrl = reader.result as string;
      this.previewVisible = true;
    };
    reader.readAsDataURL(this.selectedFile);
  }

  onPreview(): void {
    if (this.selectedFile && !this.hasUploaded) {
      this.audioPreviewUrl = URL.createObjectURL(this.selectedFile);
      this.previewVisible = true;
    }
  }

  uploadStatus: string = '';

  uploadFile(): void {
    if (!this.selectedFile) return;
  
    this.isUploading = true;
    this.uploadStatus = 'Uploading...';
  
    const formData = new FormData();
    formData.append('file', this.selectedFile);
  
    this.restService.uploadFile(this.selectedFile).subscribe({
      next: (res) => {
        console.log('Upload success:', res);
        this.hasUploaded = true;
        this.uploadStatus = 'Upload successful!';
        this.resetForm();
      },
      error: (err) => {
        console.error('Upload failed:', err);
        this.uploadStatus = 'Upload failed.';
        this.isUploading = false;
      }
    });
  }
  
  resetForm(): void {
    setTimeout(() => {
      this.selectedFile = null;
      this.audioPreviewUrl = null;
      this.previewVisible = false;
      this.isUploading = false;
      this.hasUploaded = false;
      this.uploadStatus = '';
    }, 2000); // clear UI 2 seconds after success
  }
}

