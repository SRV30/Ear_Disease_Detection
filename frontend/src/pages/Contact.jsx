import { Helmet } from "react-helmet";

import { useState } from "react";
export default function Contact() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    subject: "",
    message: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <>
      <Helmet>
        <title>Contact | EarCare AI Clinic</title>
        <meta
          name="description"
          content="Contact EarCare AI Clinic for appointments, collaborations, or technical support related to AI-powered ear disease detection."
        />
      </Helmet>

      <section className="max-w-6xl mx-auto px-4 py-12 space-y-10">
        <div className="text-center max-w-3xl mx-auto mb-4">
          <h2 className="text-4xl font-extrabold text-slate-900 mb-3">
            Contact EarCare AI Clinic
          </h2>
          <p className="text-sm md:text-base text-slate-600 leading-relaxed">
            Have questions about AI diagnosis, want to collaborate, or need support?
            Reach out to us and our team will get back within 24 hours on working days.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-slate-100 p-6 md:p-8">
            <h3 className="text-lg md:text-xl font-semibold text-slate-900 mb-4">
              Quick Enquiry Form
            </h3>
            <p className="text-xs md:text-sm text-slate-500 mb-6">
              Share your details and query below. This form is for demo purposes only
              in this project – actual hospital systems may connect this to email or CRM.
            </p>

            <form className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="md:col-span-1">
                <label className="block text-slate-600 mb-1">Full Name</label>
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="Your full name"
                />
              </div>
              <div className="md:col-span-1">
                <label className="block text-slate-600 mb-1">Email Address</label>
                <input
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="you@example.com"
                />
              </div>
              <div className="md:col-span-1">
                <label className="block text-slate-600 mb-1">Phone Number</label>
                <input
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="+91 9XXXXXXXXX"
                />
              </div>
              <div className="md:col-span-1">
                <label className="block text-slate-600 mb-1">Subject</label>
                <input
                  name="subject"
                  value={form.subject}
                  onChange={handleChange}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="Appointment / Partnership / Support"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-slate-600 mb-1">Message</label>
                <textarea
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  rows="4"
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  placeholder="Write your message here..."
                />
              </div>
              <div className="md:col-span-2 flex flex-wrap items-center justify-between gap-3 mt-2">
                <button
                  type="button"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2.5 rounded-xl shadow-md text-sm"
                >
                  Submit Enquiry
                </button>
                <p className="text-[11px] text-slate-500">
                  By submitting, you agree that this is a demo form for an academic project.
                </p>
              </div>
            </form>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-3">
                Clinic Details
              </h3>
              <div className="space-y-3 text-sm text-slate-600">
                <p>
                  <span className="font-semibold text-slate-800">Address:</span><br />
                  Hall 1,<br />
                  Indian Institute of Information Technology, Design & Manufacturing Jabalpur (IIITDMJ)
                </p>
                <p>
                  <span className="font-semibold text-slate-800">Phone:</span><br />
                  +91-9182637455
                </p>
                <p>
                  <span className="font-semibold text-slate-800">Email:</span><br />
                  care@earcare-ai.com
                </p>
              </div>
            </div>

            <div className="bg-linear-to-r from-indigo-600 to-blue-500 rounded-3xl shadow-xl p-5 text-white text-sm space-y-2">
              <p className="font-semibold text-base">Clinic Hours (Demo)</p>
              <p>Mon - Fri: 9:00 AM – 6:00 PM</p>
              <p>Sat: 10:00 AM – 2:00 PM</p>
              <p className="text-xs opacity-90">
                This is a student project UI. For real medical emergencies, please
                visit the nearest hospital or call your local emergency number.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">
              Find Us on Google Maps
            </h3>
            <p className="text-xs md:text-sm text-slate-600 mb-3">
              Open Google Maps to view ENT hospitals and clinical facilities around your area.
              In a real deployment, this section can be configured to show the exact clinic location.
            </p>
            <a
              href="https://www.google.com/maps/search/ENT+Hospital/"
              target="_blank"
              rel="noreferrer"
              className="inline-block bg-red-500 hover:bg-red-600 text-white font-semibold px-5 py-2 rounded-xl text-sm shadow-md"
            >
              Open in Google Maps
            </a>
          </div>

          <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-0 overflow-hidden">
            <div className="h-10 bg-slate-100 px-4 flex items-center text-xs font-semibold text-slate-500">
              Location Preview (Demo)
            </div>
            <div className="h-64 bg-slate-200 flex items-center justify-center text-slate-500 text-xs">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3667.8146199961125!2d80.0247353!3d23.1769651!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3981a94397365dd3%3A0x5f9aeb812c2678c9!2sIIITDM%20Jabalpur!5e0!3m2!1sen!2sin!4v1774825346966!5m2!1sen!2sin"
                width="600"
                height="450"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              ></iframe>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}