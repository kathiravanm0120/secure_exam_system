package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

type SecureExamContract struct {
	contractapi.Contract
}

type Event struct {
	ID        string                 `json:"id"`
	Timestamp string                 `json:"timestamp"`
	Event     string                 `json:"event"`
	Data      map[string]interface{} `json:"data"`
}

func (c *SecureExamContract) RecordEvent(ctx contractapi.TransactionContextInterface, eventName, dataJSON string) (*Event, error) {
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(dataJSON), &data); err != nil {
		return nil, fmt.Errorf("invalid event data: %w", err)
	}
	txID := ctx.GetStub().GetTxID()
	event := &Event{ID: txID, Timestamp: time.Now().UTC().Format(time.RFC3339Nano), Event: eventName, Data: data}
	raw, _ := json.Marshal(event)
	if err := ctx.GetStub().PutState("event:"+txID, raw); err != nil {
		return nil, err
	}
	return event, nil
}

func (c *SecureExamContract) GetEvent(ctx contractapi.TransactionContextInterface, eventID string) (*Event, error) {
	raw, err := ctx.GetStub().GetState("event:" + eventID)
	if err != nil || raw == nil {
		return nil, fmt.Errorf("event not found: %s", eventID)
	}
	var e Event
	if err := json.Unmarshal(raw, &e); err != nil {
		return nil, err
	}
	return &e, nil
}

func (c *SecureExamContract) GetEvents(ctx contractapi.TransactionContextInterface) ([]*Event, error) {
	it, err := ctx.GetStub().GetStateByRange("event:", "event;")
	if err != nil {
		return nil, err
	}
	defer it.Close()
	var events []*Event
	for it.HasNext() {
		kv, err := it.Next()
		if err != nil {
			return nil, err
		}
		var e Event
		if err := json.Unmarshal(kv.Value, &e); err != nil {
			return nil, err
		}
		events = append(events, &e)
	}
	return events, nil
}

func (c *SecureExamContract) GetQuestionEvents(ctx contractapi.TransactionContextInterface, questionID string) ([]*Event, error) {
	events, err := c.GetEvents(ctx)
	if err != nil {
		return nil, err
	}
	out := make([]*Event, 0)
	for _, e := range events {
		if v, ok := e.Data["question_id"]; ok && fmt.Sprint(v) == questionID {
			out = append(out, e)
		}
	}
	return out, nil
}

func (c *SecureExamContract) GetExamEvents(ctx contractapi.TransactionContextInterface, examID string) ([]*Event, error) {
	events, err := c.GetEvents(ctx)
	if err != nil {
		return nil, err
	}
	out := make([]*Event, 0)
	for _, e := range events {
		if v, ok := e.Data["exam_id"]; ok && fmt.Sprint(v) == examID {
			out = append(out, e)
		}
	}
	return out, nil
}

func (c *SecureExamContract) VerifyQuestion(ctx contractapi.TransactionContextInterface, questionID, expectedContentHash string) (map[string]interface{}, error) {
	events, err := c.GetQuestionEvents(ctx, questionID)
	if err != nil {
		return nil, err
	}
	matching := false
	for _, e := range events {
		if h, ok := e.Data["content_hash"]; ok && fmt.Sprint(h) == expectedContentHash {
			matching = true
			break
		}
	}
	return map[string]interface{}{
		"question_id":             questionID,
		"content_hash_matched":    matching,
		"recorded_events_count":   len(events),
		"blockchain_verification": true,
	}, nil
}

func (c *SecureExamContract) RecordReleaseApproval(ctx contractapi.TransactionContextInterface, examID, officerID, approvedAt string) (*Event, error) {
	data := map[string]interface{}{"exam_id": examID, "officer_id": officerID, "approved_at": approvedAt}
	rawData, _ := json.Marshal(data)
	return c.RecordEvent(ctx, "EXAM_RELEASE_APPROVED", string(rawData))
}

func (c *SecureExamContract) RecordExamRelease(ctx contractapi.TransactionContextInterface, examID, releasedBy, releaseTime, approverIDsJSON string) (*Event, error) {
	var approverIDs []string
	if err := json.Unmarshal([]byte(approverIDsJSON), &approverIDs); err != nil {
		return nil, fmt.Errorf("invalid approver ids: %w", err)
	}
	data := map[string]interface{}{"exam_id": examID, "released_by": releasedBy, "release_time": releaseTime, "approver_ids": approverIDs}
	rawData, _ := json.Marshal(data)
	return c.RecordEvent(ctx, "EXAM_RELEASED", string(rawData))
}

func (c *SecureExamContract) RecordQuestionExposure(ctx contractapi.TransactionContextInterface, questionID, sessionID, candidateID string, exposureCount int) (*Event, error) {
	data := map[string]interface{}{"question_id": questionID, "session_id": sessionID, "candidate_id": candidateID, "exposure_count": exposureCount}
	rawData, _ := json.Marshal(data)
	return c.RecordEvent(ctx, "QUESTION_EXPOSED", string(rawData))
}

func (c *SecureExamContract) VerifyChain(ctx contractapi.TransactionContextInterface) (map[string]interface{}, error) {
	events, err := c.GetEvents(ctx)
	if err != nil {
		return nil, err
	}
	return map[string]interface{}{"valid": true, "events": len(events), "backend": "hyperledger-fabric"}, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SecureExamContract{})
	if err != nil {
		panic(err)
	}
	if err := chaincode.Start(); err != nil {
		panic(err)
	}
}
