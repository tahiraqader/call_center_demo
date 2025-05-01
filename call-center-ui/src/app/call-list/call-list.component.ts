
import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest-service.service';
import { CallStateService } from '../services/call-state.service';
import { CallRecord } from '../data/callRecord';

@Component({
  selector: 'app-call-list',
  templateUrl: './call-list.component.html',
  styleUrls: ['./call-list.component.scss']
})
export class CallListComponent implements OnInit {
  calls: CallRecord[] = [];

  constructor(private callService: RestService, private callState: CallStateService) {}

  ngOnInit(): void {
    this.fetchCalls();
    this.callState.callsUpdated$.subscribe(() => this.fetchCalls());
  }

  fetchCalls() {
    this.callService.getCalls().subscribe(data => {
      this.calls = data;
    });
  }

  editCall(call: any, field: string) {
    const newVal = prompt(`Edit ${field}`, call[field]);
    if (newVal !== null) {
      this.callService.updateCall(call._id, { [field]: newVal }).subscribe(() => this.fetchCalls());
    }
  }

  deleteCall(id: string) {
    if (confirm('Are you sure you want to delete this call?')) {
      this.callService.deleteCall(id).subscribe(() => this.fetchCalls());
    }
  }
}
