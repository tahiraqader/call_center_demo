import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { CallRecord } from '../data/callRecord';
import { environment } from 'src/environments/environment';
import { tap, map, switchMap } from "rxjs/operators";


@Injectable({
  providedIn: 'root'
})
export class RestService {
  private apiUrl = environment.apiUrl; // Your Flask server URL
  private dataAdded = new Subject<any>(); // Observable for change notifications

  dataAdded$ = this.dataAdded.asObservable();

  constructor(private http: HttpClient) {}

  // Add a new call
  uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/create`, formData).pipe(
      tap((data)=>this.dataAdded.next(data)) // Notify listeners other then the caller
    );
  }

 
  // GET: Fetch all calls
  getCalls(): Observable<any[]> {
    return this.http.get<CallRecord[]>(`${this.apiUrl}/calls`);
  }

  // PUT: Update a specific field of a call by ID
  updateSummary(id: string, update: { [key: string]: any }): Observable<any> {
    return this.http.put(`${this.apiUrl}/update/${id}`, update);
  }

  // DELETE: Delete a call by ID
  deleteCall(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/delete/${id}`);
  }
}


