
import { Component } from '@angular/core';
import { RestService } from '../services/rest-service.service';
@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  selectedFile: File | null = null;
  myAudioPreviewUrl: string | null = null;
  isUploading = false;
  previewVisible: boolean = false;
  hasUploaded: boolean = false;

  constructor(private restService: RestService) { }

  onFileSelected(event: any): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.selectedFile = file;

      // Revoke the old preview URL (if any) to avoid memory leaks
      if (this.myAudioPreviewUrl) {
        URL.revokeObjectURL(this.myAudioPreviewUrl);
      }

      this.myAudioPreviewUrl = URL.createObjectURL(file);
      this.previewVisible = true;
      this.hasUploaded = false;
      console.log('Preview URL:', this.myAudioPreviewUrl);
      console.log('Selected file:', this.selectedFile);
    }
  }
  previewAudio(): void {
    if (!this.selectedFile) return;

    const reader = new FileReader();
    reader.onload = () => {
      // this.myAudioPreviewUrl = reader.result as string;
      this.previewVisible = true;
    };
    reader.readAsDataURL(this.selectedFile);
  }

  onPreview(): void {
    if (this.selectedFile && !this.hasUploaded) {
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
      this.myAudioPreviewUrl = null;
      this.previewVisible = false;
      this.isUploading = false;
      this.hasUploaded = false;
      this.uploadStatus = '';
    }, 2000); // clear UI 2 seconds after success
  }
}

