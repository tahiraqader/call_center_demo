import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CallStateService {
  private callsUpdated = new BehaviorSubject<void>(undefined);
  public callsUpdated$ = this.callsUpdated.asObservable();

  notifyCallsUpdated() {
    this.callsUpdated.next();
  }
}
