import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Shield, MessageSquare, Calendar, FileText, Award, Lock, Users, CheckCircle } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[--sand-50] to-[--background]">
      {/* Header/Nav */}
      <header className="border-b border-[--border] bg-[--background]/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <h2 className="text-xl font-[--font-weight-semibold] text-[--foreground]">
            Mental Health Assistant
          </h2>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm">Sign In</Button>
            <Button variant="primary" size="sm">Get Started</Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 md:py-32">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-[--font-weight-semibold] text-[--foreground] mb-6 leading-tight">
            Your Path to Better Mental Wellness
          </h1>
          <p className="text-xl text-[--muted-foreground] mb-8 leading-relaxed">
            Connect with licensed mental health specialists, receive AI-powered support, and take control of your mental health journey—all in one secure, compassionate platform.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button variant="primary" size="lg">Start Your Journey</Button>
            <Button variant="secondary" size="lg">Learn More</Button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-4">How It Works</h2>
          <p className="text-[--muted-foreground] max-w-2xl mx-auto">
            Getting the mental health support you need is simple, secure, and completely confidential.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="size-16 mx-auto mb-4 rounded-full bg-[--primary-light] flex items-center justify-center">
              <Users className="size-8 text-[--primary]" />
            </div>
            <h3 className="text-xl font-[--font-weight-semibold] text-[--foreground] mb-2">1. Create Your Profile</h3>
            <p className="text-[--muted-foreground]">
              Sign up securely and tell us about your needs and preferences. Your information is protected with bank-level encryption.
            </p>
          </div>

          <div className="text-center">
            <div className="size-16 mx-auto mb-4 rounded-full bg-[--primary-light] flex items-center justify-center">
              <MessageSquare className="size-8 text-[--primary]" />
            </div>
            <h3 className="text-xl font-[--font-weight-semibold] text-[--foreground] mb-2">2. Get Support</h3>
            <p className="text-[--muted-foreground]">
              Use our AI assistant for immediate support and guidance, or browse our network of licensed specialists.
            </p>
          </div>

          <div className="text-center">
            <div className="size-16 mx-auto mb-4 rounded-full bg-[--primary-light] flex items-center justify-center">
              <Calendar className="size-8 text-[--primary]" />
            </div>
            <h3 className="text-xl font-[--font-weight-semibold] text-[--foreground] mb-2">3. Book & Connect</h3>
            <p className="text-[--muted-foreground]">
              Schedule appointments with specialists that match your needs. Sessions available via video, phone, or in-person.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24 bg-[--card]">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-4">Comprehensive Mental Health Support</h2>
          <p className="text-[--muted-foreground] max-w-2xl mx-auto">
            Everything you need to manage your mental wellness in one trusted platform.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="size-12 rounded-[--radius-lg] bg-[--primary-light] flex items-center justify-center flex-shrink-0">
                  <MessageSquare className="size-6 text-[--primary]" />
                </div>
                <div>
                  <CardTitle>AI Chat Support</CardTitle>
                  <p className="text-sm text-[--muted-foreground] mt-2">
                    Get immediate, compassionate support 24/7. Our AI assistant helps you process emotions, provides coping strategies, and knows when to recommend professional care.
                  </p>
                </div>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="size-12 rounded-[--radius-lg] bg-[--primary-light] flex items-center justify-center flex-shrink-0">
                  <Users className="size-6 text-[--primary]" />
                </div>
                <div>
                  <CardTitle>Licensed Specialists</CardTitle>
                  <p className="text-sm text-[--muted-foreground] mt-2">
                    Browse and connect with verified mental health professionals. Filter by specialty, location, availability, and more to find your perfect match.
                  </p>
                </div>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="size-12 rounded-[--radius-lg] bg-[--primary-light] flex items-center justify-center flex-shrink-0">
                  <Calendar className="size-6 text-[--primary]" />
                </div>
                <div>
                  <CardTitle>Easy Appointment Booking</CardTitle>
                  <p className="text-sm text-[--muted-foreground] mt-2">
                    Schedule, reschedule, or cancel appointments with ease. Receive reminders and manage everything from your dashboard.
                  </p>
                </div>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="size-12 rounded-[--radius-lg] bg-[--primary-light] flex items-center justify-center flex-shrink-0">
                  <FileText className="size-6 text-[--primary]" />
                </div>
                <div>
                  <CardTitle>Progress Tracking</CardTitle>
                  <p className="text-sm text-[--muted-foreground] mt-2">
                    Track your mood, view session summaries, and monitor your mental health journey with clear, actionable insights.
                  </p>
                </div>
              </div>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Trust & Privacy */}
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-4">Your Privacy & Security</h2>
          <p className="text-[--muted-foreground] max-w-2xl mx-auto">
            We take your privacy seriously. Your mental health journey is protected with industry-leading security measures.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="flex items-start gap-4">
            <Shield className="size-6 text-[--primary] flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-2">HIPAA Compliant</h4>
              <p className="text-sm text-[--muted-foreground]">
                Full compliance with healthcare privacy regulations to protect your personal health information.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <Lock className="size-6 text-[--primary] flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-2">End-to-End Encryption</h4>
              <p className="text-sm text-[--muted-foreground]">
                All communications and data are encrypted using bank-level security standards.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <Award className="size-6 text-[--primary] flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-2">Verified Providers</h4>
              <p className="text-sm text-[--muted-foreground]">
                All mental health specialists are licensed, verified, and meet our rigorous standards.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Specialist Teaser */}
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24 bg-gradient-to-br from-[--teal-700] to-[--teal-900] rounded-[--radius-xl] text-white">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-[--font-weight-semibold] mb-4">Are You a Mental Health Professional?</h2>
          <p className="text-lg text-[--teal-100] mb-8">
            Join our network of trusted specialists. Help more people while managing your practice with powerful, intuitive tools.
          </p>
          <div className="flex items-center justify-center gap-4">
            <CheckCircle className="size-5" />
            <span>Flexible scheduling</span>
          </div>
          <div className="flex items-center justify-center gap-4 mt-3">
            <CheckCircle className="size-5" />
            <span>Secure client communication</span>
          </div>
          <div className="flex items-center justify-center gap-4 mt-3">
            <CheckCircle className="size-5" />
            <span>Practice management tools</span>
          </div>
          <Button variant="secondary" size="lg" className="mt-8">Learn More About Joining</Button>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24 text-center">
        <h2 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-4">
          Ready to Take the First Step?
        </h2>
        <p className="text-[--muted-foreground] mb-8 max-w-2xl mx-auto">
          Your mental health matters. Join thousands who have found support, guidance, and healing through our platform.
        </p>
        <Button variant="primary" size="lg">Get Started Today</Button>
      </section>

      {/* Footer */}
      <footer className="border-t border-[--border] bg-[--card] py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-[--font-weight-semibold] text-[--foreground] mb-4">Mental Health Assistant</h3>
              <p className="text-sm text-[--muted-foreground]">
                Compassionate, professional mental health support when you need it most.
              </p>
            </div>

            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-[--muted-foreground]">
                <li><a href="#" className="hover:text-[--primary]">Features</a></li>
                <li><a href="#" className="hover:text-[--primary]">Pricing</a></li>
                <li><a href="#" className="hover:text-[--primary]">For Specialists</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-[--muted-foreground]">
                <li><a href="#" className="hover:text-[--primary]">Help Center</a></li>
                <li><a href="#" className="hover:text-[--primary]">Crisis Resources</a></li>
                <li><a href="#" className="hover:text-[--primary]">Blog</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-[--font-weight-semibold] text-[--foreground] mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-[--muted-foreground]">
                <li><a href="#" className="hover:text-[--primary]">About Us</a></li>
                <li><a href="#" className="hover:text-[--primary]">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-[--primary]">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-[--border] text-center text-sm text-[--muted-foreground]">
            <p>© 2026 Mental Health Assistant. All rights reserved.</p>
            <p className="mt-2">If you're in crisis, please call 988 (Suicide & Crisis Lifeline) or go to your nearest emergency room.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
