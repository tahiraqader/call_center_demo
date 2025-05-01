import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CallRecord } from '../data/callRecord';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class RestService {
  private apiUrl = environment.apiUrl; // Your Flask server URL

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/create`, formData);
  }

  // GET: Fetch all calls
  getCalls(): Observable<any[]> {
    return this.http.get<CallRecord[]>(`${this.apiUrl}/calls`);
  }

  // PUT: Update a specific field of a call by ID
  updateCall(id: string, update: { [key: string]: any }): Observable<any> {
    return this.http.put(`${this.apiUrl}/update/${id}`, update);
  }

  // DELETE: Delete a call by ID
  deleteCall(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/delete/${id}`);
  }
}
