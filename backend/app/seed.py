"""Database seeding script for end-to-end demo scenario (Phase 28).

Creates Admin, Setters, Reviewers, Officers, Candidates, Exam Centre, CBT Device,
and 30+ Computer Science questions across topics and difficulty levels.
"""
from __future__ import annotations

import datetime
from datetime import timezone
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models.models import (
    CentreDevice,
    Exam,
    ExamCandidateAssignment,
    ExamCentre,
    ExamCentreAssignment,
    Question,
    QuestionReview,
    User,
)
from app.security.auth import hash_password
from app.security.encryption import _ensure_authority_keypair, encrypt_question
from app.blockchain.service import add_event


def seed_database():
    """Populate database with complete seed data."""
    _ensure_authority_keypair()
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("[SEED] Seeding Secure Exam System database...")

        # 1. Create Users
        users_data = [
            ("System Admin", "admin@example.com", "password123", "ADMIN"),
            ("Setter Alice", "setter_a@example.com", "password123", "SETTER"),
            ("Setter Bob", "setter_b@example.com", "password123", "SETTER"),
            ("Reviewer Charlie", "reviewer_a@example.com", "password123", "REVIEWER"),
            ("Reviewer Diana", "reviewer_b@example.com", "password123", "REVIEWER"),
            ("Officer Frank", "officer_a@example.com", "password123", "EXAM_OFFICER"),
            ("Officer Grace", "officer_b@example.com", "password123", "EXAM_OFFICER"),
            ("Candidate Eve", "candidate_a@example.com", "password123", "CANDIDATE"),
            ("Candidate Mallory", "candidate_b@example.com", "password123", "CANDIDATE"),
        ]

        users = {}
        for name, email, password, role in users_data:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    role=role,
                )
                db.add(user)
                db.flush()
            users[email] = user

        db.commit()
        print(f"  + {len(users)} Users created/verified")

        admin = users["admin@example.com"]
        setter_a = users["setter_a@example.com"]
        setter_b = users["setter_b@example.com"]
        reviewer_a = users["reviewer_a@example.com"]
        reviewer_b = users["reviewer_b@example.com"]
        candidate_a = users["candidate_a@example.com"]

        # 2. Create Centre and Device
        centre = db.query(ExamCentre).filter(ExamCentre.code == "CTR-001").first()
        if not centre:
            centre = ExamCentre(code="CTR-001", name="Coimbatore CBT Centre 001", status="ACTIVE")
            db.add(centre)
            db.flush()
            add_event("CENTRE_CREATED", {"centre_id": centre.id, "code": centre.code, "created_by": admin.id})

        import hashlib
        raw_device_token = "SECURE_DEV_TOKEN_0001"
        device_token_hash = hashlib.sha256(raw_device_token.encode("utf-8")).hexdigest()

        device = db.query(CentreDevice).filter(CentreDevice.device_code == "DEV-0001").first()
        if not device:
            device = CentreDevice(
                centre_id=centre.id,
                device_code="DEV-0001",
                device_token_hash=device_token_hash,
                status="ACTIVE",
            )
            db.add(device)
            db.flush()
            add_event("CENTRE_DEVICE_REGISTERED", {"centre_id": centre.id, "device_id": device.id, "registered_by": admin.id})

        db.commit()
        print("  + Exam Centre (CTR-001) & Registered Device (DEV-0001) created")

        # 3. Create 30 Sample Questions in Computer Science
        sample_questions_data = [
            # Data Structures - EASY
            ("What is the time complexity of array lookup by index?", "O(1)", "Data Structures", "EASY"),
            ("Which data structure follows LIFO (Last In First Out)?", "Stack", "Data Structures", "EASY"),
            ("Which data structure follows FIFO (First In First Out)?", "Queue", "Data Structures", "EASY"),
            ("What is the worst-case lookup time in a hash table?", "O(n)", "Data Structures", "EASY"),
            ("What structure connects nodes via pointers?", "Linked List", "Data Structures", "EASY"),
            # Data Structures - MEDIUM
            ("What is the average time complexity of searching in a Binary Search Tree?", "O(log n)", "Data Structures", "MEDIUM"),
            ("Which tree structure self-balances using rotations?", "AVL Tree", "Data Structures", "MEDIUM"),
            ("What algorithm finds the shortest path in a weighted graph?", "Dijkstra Algorithm", "Data Structures", "MEDIUM"),
            ("What data structure is used for Breadth First Search?", "Queue", "Data Structures", "MEDIUM"),
            ("What data structure is used for Depth First Search?", "Stack", "Data Structures", "MEDIUM"),
            # Data Structures - HARD
            ("What is the amortized complexity of insertion in a dynamic array?", "O(1)", "Data Structures", "HARD"),
            ("What structure maintains a max or min property at the root?", "Heap", "Data Structures", "HARD"),
            ("Which tree structure guarantees O(log n) operations with red/black nodes?", "Red-Black Tree", "Data Structures", "HARD"),
            ("What structure is used to solve Disjoint Set Union operations in linear time?", "Union-Find with Path Compression", "Data Structures", "HARD"),
            ("What data structure compresses sparse matrices effectively?", "CSR (Compressed Sparse Row)", "Data Structures", "HARD"),
            # Algorithms - EASY
            ("What sorting algorithm compares adjacent elements and swaps them?", "Bubble Sort", "Algorithms", "EASY"),
            ("What is the time complexity of Linear Search?", "O(n)", "Algorithms", "EASY"),
            ("What sorting algorithm divides the list into halves recursively?", "Merge Sort", "Algorithms", "EASY"),
            ("What sorting algorithm selects the minimum element in each pass?", "Selection Sort", "Algorithms", "EASY"),
            ("What search algorithm requires a sorted array?", "Binary Search", "Algorithms", "EASY"),
            # Algorithms - MEDIUM
            ("What is the average time complexity of QuickSort?", "O(n log n)", "Algorithms", "MEDIUM"),
            ("Which paradigm does Knapsack Problem dynamic programming use?", "Dynamic Programming", "Algorithms", "MEDIUM"),
            ("What algorithm finds all-pairs shortest paths in a graph?", "Floyd-Warshall Algorithm", "Algorithms", "MEDIUM"),
            ("What greedy algorithm finds the Minimum Spanning Tree using edges?", "Kruskal Algorithm", "Algorithms", "MEDIUM"),
            ("What algorithm finds MST using growing tree of vertices?", "Prim Algorithm", "Algorithms", "MEDIUM"),
            # Algorithms - HARD
            ("What is the worst-case time complexity of QuickSort?", "O(n^2)", "Algorithms", "HARD"),
            ("Which string matching algorithm uses prefix function values?", "KMP Algorithm", "Algorithms", "HARD"),
            ("What algorithm computes maximum flow in a network?", "Ford-Fulkerson Algorithm", "Algorithms", "HARD"),
            ("What technique reduces state space in game trees?", "Alpha-Beta Pruning", "Algorithms", "HARD"),
            ("What complexity class contains decision problems solvable in polynomial time?", "P", "Algorithms", "HARD"),
        ]

        question_count = 0
        for idx, (content, answer, topic, diff) in enumerate(sample_questions_data):
            # Alternate setters
            creator = setter_a if idx % 2 == 0 else setter_b
            reviewer = reviewer_a if idx % 2 == 0 else reviewer_b

            encrypted = encrypt_question(content, answer)
            existing = db.query(Question).filter(Question.content_hash == encrypted["content_hash"]).first()
            if not existing:
                q = Question(
                    encrypted_content=encrypted["encrypted_content"],
                    encryption_nonce=encrypted["encryption_nonce"],
                    wrapped_key=encrypted["wrapped_key"],
                    content_hash=encrypted["content_hash"],
                    crypto_version=encrypted["crypto_version"],
                    subject="Computer Science",
                    topic=topic,
                    difficulty=diff,
                    created_by=creator.id,
                    reviewer_id=reviewer.id,
                    status="APPROVED",
                    exposure_status="ACTIVE",
                    exposure_count=0,
                )
                db.add(q)
                db.flush()

                # Record Review
                rev = QuestionReview(
                    question_id=q.id,
                    reviewer_id=reviewer.id,
                    decision="APPROVE",
                    comments="Question content approved during seeding.",
                )
                db.add(rev)

                add_event("QUESTION_CREATED", {"question_id": q.id, "content_hash": q.content_hash, "subject": "Computer Science", "topic": topic, "difficulty": diff})
                add_event("QUESTION_APPROVED", {"question_id": q.id, "content_hash": q.content_hash, "reviewer_id": reviewer.id, "decision": "APPROVE"})
                question_count += 1

        db.commit()
        print(f"  + {question_count} Computer Science questions encrypted and approved")

        # 4. Create Scheduled Exam with Blueprint
        exam = db.query(Exam).filter(Exam.name == "Computer Science Core Examination 2026").first()
        if not exam:
            now = datetime.datetime.now(timezone.utc)
            starts_at = now - datetime.timedelta(minutes=5)
            ends_at = now + datetime.timedelta(hours=3)

            blueprint = [
                {"topic": "Data Structures", "difficulty": "EASY", "count": 2},
                {"topic": "Data Structures", "difficulty": "MEDIUM", "count": 2},
                {"topic": "Algorithms", "difficulty": "EASY", "count": 2},
                {"topic": "Algorithms", "difficulty": "MEDIUM", "count": 2},
            ]

            exam = Exam(
                name="Computer Science Core Examination 2026",
                subject="Computer Science",
                starts_at=starts_at,
                ends_at=ends_at,
                blueprint=blueprint,
                created_by=admin.id,
                status="SCHEDULED",
            )
            db.add(exam)
            db.flush()
            add_event("EXAM_CREATED", {"exam_id": exam.id, "name": exam.name, "subject": exam.subject, "created_by": admin.id, "blueprint": blueprint})

        db.commit()

        # Assign centre and candidate
        ca = db.query(ExamCentreAssignment).filter(ExamCentreAssignment.exam_id == exam.id, ExamCentreAssignment.centre_id == centre.id).first()
        if not ca:
            ca = ExamCentreAssignment(exam_id=exam.id, centre_id=centre.id)
            db.add(ca)

        c_assign = db.query(ExamCandidateAssignment).filter(ExamCandidateAssignment.exam_id == exam.id, ExamCandidateAssignment.candidate_id == candidate_a.id).first()
        if not c_assign:
            c_assign = ExamCandidateAssignment(
                exam_id=exam.id,
                candidate_id=candidate_a.id,
                centre_id=centre.id,
                seat_number="SEAT-A-01",
                identity_status="VERIFIED",
                verified_at=datetime.datetime.now(timezone.utc),
                verified_by=admin.id,
            )
            db.add(c_assign)

        db.commit()
        print(f"  + Exam #{exam.id} ('{exam.name}') created, centre assigned & Candidate verified")
        print("\n[SEED SUCCESS] Environment ready for End-to-End demonstration.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
