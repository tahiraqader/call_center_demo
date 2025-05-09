
import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest-service.service';
import { CallRecord } from '../data/callRecord';
import { ChangeDetectorRef } from '@angular/core';
import { NgZone } from '@angular/core';


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
  totalPages: number = 1;

  pagedCalls: CallRecord[] = []; // items to show on current page


  constructor(private callService: RestService, private cdr: ChangeDetectorRef, private zone: NgZone) { }

  ngOnInit() {
    this.fetchCalls();
    this.callService.dataAdded$.subscribe((data) => {
      this.calls.unshift(data);
      this.currentPage = 1;
      this.updatePagedCalls();  // Force to show latest call 
      this.cdr.detectChanges(); // adding to beginning might not trigger change detection.
    });
  }

  // to get the calls first time
  fetchCalls() {
    this.callService.getCalls().subscribe(data => {
      this.calls = data;
      this.updatePagedCalls(); // show the first page only
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
        .subscribe((data) => {
          console.log("=======date", data)
          const index = this.calls.findIndex(item => item._id === this.editingCallId);
          if (index != -1) {
            this.calls[index].summary = data.summary;
            this.calls[index].action_items = data.action_items;
            console.log(this.calls[index])
          }
        });
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

  updatePagedCalls() {
    this.totalPages = Math.ceil(this.calls.length / this.pageSize);
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    this.pagedCalls = this.calls.slice(start, end);
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePagedCalls();
    }
  }

  nextPage() {
    this.goToPage(this.currentPage + 1);
  }

  prevPage() {
    this.goToPage(this.currentPage - 1);
  }
}
