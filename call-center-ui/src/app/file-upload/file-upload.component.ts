// import { Component } from '@angular/core';
// import { RestService } from '../services/rest-service.service';

// @Component({
//   selector: 'app-file-upload',
//   templateUrl: './file-upload.component.html',
// })
// export class FileUploadComponent {
//   selectedFile: File | null = null;

//   constructor(private restService: RestService) {}

//   onFileSelected(event: any) {
//     this.selectedFile = event.target.files[0];
//   }

//   onUpload() {
//     if (this.selectedFile) {
//       this.restService.uploadFile(this.selectedFile).subscribe(
//         response => console.log('Upload success', response),
//         error => console.error('Upload error', error)
//       );
//     }
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
  isUploading = false;

  constructor(private restService: RestService) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  uploadFile(): void {
    if (!this.selectedFile) return;

    this.isUploading = true;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.restService.uploadFile(this.selectedFile).subscribe({
      next: (response) => {
        console.log('Upload success:', response);
      },
      error: (error) => {
        console.error('Upload error:', error);
      },
      complete: () => {
        this.isUploading = false;
        this.selectedFile = null;
      }
    });
  }
}
