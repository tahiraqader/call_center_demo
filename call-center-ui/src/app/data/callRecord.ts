export interface CallRecord {
     _id: string,                     // MongoDB ObjectId as string
     dialog: string,         // Full transcription text
     summary: string,               // Summary text
     action_items: string[],           // Action items text
     date: Date | string                    // Date of the call
     caller_sentiment: string
     agent_sentiment: string
}
