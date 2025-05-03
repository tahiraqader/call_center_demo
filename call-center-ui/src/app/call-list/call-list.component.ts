
import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest-service.service';
import { CallRecord } from '../data/callRecord';

@Component({
  selector: 'app-call-list',
  templateUrl: './call-list.component.html',
  styleUrls: ['./call-list.component.scss']
})
export class CallListComponent implements OnInit {
  calls: CallRecord[] = [];
  editingField: string | null = null;
  editValue: string = '';
  editingCallId: string = '';
  showTranscription = false;
  currentPage = 1;
  pageSize = 10;

  constructor(private callService: RestService) { }

  ngOnInit() {
    this.fetchCalls();
    this.callService.dataAdded$.subscribe((data) => {
      this.calls.push(data)

    });
  }

  // to get the calls first time
  fetchCalls() {
    this.callService.getCalls().subscribe(data => {
      this.calls = data;
    });
  }


  editField(call: any, field: string) {
    this.editingField = field;
    this.editValue = call[field];
    this.editingCallId = call._id;
  }

  saveEdit() {
    if (this.editingField) {
      this.callService
        .updateSummary(this.editingCallId, { [this.editingField]: this.editValue })
        .subscribe(() => { });
    }
    this.editingField = null;
  }

  cancelEdit() {
    this.editingField = null;
  }

  deleteCall(id: string) {
    if (confirm('Are you sure you want to delete this call?')) {
      this.callService.deleteCall(id).subscribe(() => {
        const index = this.calls.findIndex(item => item._id === id);
        if (index !== -1) {
          this.calls.splice(index, 1);
        }
      });
    }
  }

  showTranscript(call: any, field: string) {
    this.showTranscription = true;
    this.editingField = field;
    this.editValue = call.dialog;
    let conversation = '';
    const dialog = call.dialog;
    for (let msg of dialog) {
      conversation = conversation + msg + '\n'
    }
    this.editValue = conversation;

  }
  closeTranscription() {
    this.editingField = null;
    this.showTranscription = false
    this.editingField = null;
  }

  getTotalPages(): number {
    return Math.ceil(this.calls.length / this.pageSize);
  }

  get pagedCalls() {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.calls.slice(start, start + this.pageSize);
  }

  nextPage() {
    if (this.currentPage < this.getTotalPages()) {
      this.currentPage++;
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }
}
