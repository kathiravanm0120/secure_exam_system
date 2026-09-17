import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ProtectedRoute } from '../components/layout/ProtectedRoute';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { Questions } from '../pages/Questions';
import { CreateQuestion } from '../pages/CreateQuestion';
import { ReviewQueue } from '../pages/ReviewQueue';
import { Exams } from '../pages/Exams';
import { CBT } from '../pages/CBT';
import { SecurityCenter } from '../pages/SecurityCenter';
import { Investigation } from '../pages/Investigation';
import { Blockchain } from '../pages/Blockchain';
import { Centres } from '../pages/Centres';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="questions" element={<Questions />} />
        <Route
          path="questions/new"
          element={
            <ProtectedRoute roles={['AUTHOR', 'ADMIN']}>
              <CreateQuestion />
            </ProtectedRoute>
          }
        />
        <Route
          path="reviews"
          element={
            <ProtectedRoute roles={['REVIEWER', 'EXAM_OFFICER', 'ADMIN']}>
              <ReviewQueue />
            </ProtectedRoute>
          }
        />
        <Route path="exams" element={<Exams />} />
        <Route path="cbt" element={<CBT />} />
        <Route
          path="security"
          element={
            <ProtectedRoute roles={['SECURITY_AUDITOR', 'ADMIN']}>
              <SecurityCenter />
            </ProtectedRoute>
          }
        />
        <Route
          path="investigation"
          element={
            <ProtectedRoute roles={['SECURITY_AUDITOR', 'ADMIN']}>
              <Investigation />
            </ProtectedRoute>
          }
        />
        <Route
          path="blockchain"
          element={
            <ProtectedRoute roles={['SECURITY_AUDITOR', 'ADMIN']}>
              <Blockchain />
            </ProtectedRoute>
          }
        />
        <Route
          path="centres"
          element={
            <ProtectedRoute roles={['EXAM_OFFICER', 'ADMIN']}>
              <Centres />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
