import { TestBed } from '@angular/core/testing';

import { CallStateService } from './call-state.service';

describe('CallStateService', () => {
  let service: CallStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CallStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
