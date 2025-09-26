import { BrowserRouter as Router, Routes, Route } from "react-router";
import { AppLayout } from "@/react-app/components/layout/AppLayout";
import { StorageProvider } from "@/react-app/context/StorageContext";
import Dashboard from "@/react-app/pages/Dashboard";
import Designer from "@/react-app/pages/Designer";
import Survey from "@/react-app/pages/Survey";
import FeatureExtraction from "@/react-app/pages/FeatureExtraction";
import FTTB from "@/react-app/pages/FTTB";
import FTTH from "@/react-app/pages/FTTH";
import Accessories from "@/react-app/pages/Accessories";

export default function App() {
  return (
    <StorageProvider>
      <Router>
        <Routes>
          {/* Dashboard - Main app selection */}
          <Route path="/" element={<Dashboard />} />
          
          {/* Individual Apps */}
          <Route path="/app/designer" element={
            <AppLayout appName="Designer" appDescription="Draw areas and extract building features">
              <Designer />
            </AppLayout>
          } />
          
          <Route path="/app/survey" element={
            <AppLayout appName="Survey" appDescription="Field data collection and validation tools">
              <Survey />
            </AppLayout>
          } />
          
          <Route path="/app/extraction" element={
            <AppLayout appName="Feature Extraction" appDescription="AI-powered infrastructure feature detection">
              <FeatureExtraction />
            </AppLayout>
          } />
          
          <Route path="/app/fttb" element={
            <AppLayout appName="FTTB" appDescription="Fiber to the building network design">
              <FTTB />
            </AppLayout>
          } />
          
          <Route path="/app/ftth" element={
            <AppLayout appName="FTTH" appDescription="Fiber to the home network planning">
              <FTTH />
            </AppLayout>
          } />
          
          <Route path="/app/accessories" element={
            <AppLayout appName="Accessories" appDescription="Network equipment and hardware management">
              <Accessories />
            </AppLayout>
          } />
        </Routes>
      </Router>
    </StorageProvider>
  );
}
