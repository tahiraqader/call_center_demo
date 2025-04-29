import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { CallListComponent } from './call-list/call-list.component';
import { AppRoutingModule } from './app-routing.module';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    CallListComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,   // 👈 Important
    AppRoutingModule    // 👈 here
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
