import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AppLayout } from "@/react-app/components/layout/AppLayout";
import { StorageProvider } from "@/react-app/context/StorageContext";
import Dashboard from "@/react-app/pages/dashboard";
import Features from "@/react-app/pages/features";
import Survey from "@/react-app/pages/survey";
import { FTTB, FTTH, Accessories } from "@/react-app/pages/fiber";
import Learn from "@/react-app/pages/learn";

export default function App() {
  return (
    <StorageProvider>
      <Router>
        <Routes>
          {/* Dashboard - Main app selection */}
          <Route path="/" element={<Dashboard />} />
          
          {/* Individual Apps */}
          <Route path="/features" element={
            <AppLayout appName="Features" appDescription="Extract buildings, roads and landmarks automatically">
              <Features />
            </AppLayout>
          } />
          
          <Route path="/accessories" element={
            <AppLayout appName="Accessories" appDescription="Network equipment and hardware management">
              <Accessories />
            </AppLayout>
          } />
          
          <Route path="/ftth" element={
            <AppLayout appName="FTTH" appDescription="Fiber to the home network planning">
              <FTTH />
            </AppLayout>
          } />
          
          <Route path="/fttb" element={
            <AppLayout appName="FTTB" appDescription="Fiber to the building network design">
              <FTTB />
            </AppLayout>
          } />
          
          <Route path="/survey" element={
            <AppLayout appName="Survey" appDescription="Field data collection and validation tools">
              <Survey />
            </AppLayout>
          } />
          
          <Route path="/learn" element={
            <AppLayout appName="Learn" appDescription="Training materials and documentation">
              <Learn />
            </AppLayout>
          } />
        </Routes>
      </Router>
    </StorageProvider>
  );
}
