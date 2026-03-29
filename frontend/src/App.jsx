import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Diagnose from "./pages/Diagnose";
import Result from "./pages/Result";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Privacy from "./pages/Privacy";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-linear-to-br from-blue-100 via-white to-purple-100">
        <Navbar />

        <main className="flex-1 px-4 py-6">
          <div className="max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<Home />} />

              <Route
                path="/diagnose"
                element={
                  <ProtectedRoute>
                    <Diagnose />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/result"
                element={
                  <ProtectedRoute>
                    <Result />
                  </ProtectedRoute>
                }
              />

              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </div>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;