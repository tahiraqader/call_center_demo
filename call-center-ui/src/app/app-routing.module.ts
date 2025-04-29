import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { CallListComponent } from './call-list/call-list.component';

const routes: Routes = [
  { path: 'upload', component: FileUploadComponent },
  { path: 'calls', component: CallListComponent },
  { path: '', redirectTo: '/upload', pathMatch: 'full' }, // Default to upload
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
