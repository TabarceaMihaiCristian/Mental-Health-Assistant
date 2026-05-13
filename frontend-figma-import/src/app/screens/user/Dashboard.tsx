import { Sidebar } from "../../components/layout/Sidebar";
import { Header } from "../../components/layout/Header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Avatar } from "../../components/ui/Avatar";
import { Calendar, MessageSquare, Users, FileText, Clock, TrendingUp } from "lucide-react";

export default function UserDashboard() {
  return (
    <div className="flex min-h-screen bg-[--background]">
      <Sidebar role="user" />

      <div className="flex-1">
        <Header userName="Sarah Johnson" showSearch={false} />

        <main className="p-8">
          {/* Welcome Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
              Welcome back, Sarah
            </h1>
            <p className="text-[--muted-foreground]">
              Here's what's happening with your mental health journey today
            </p>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card className="hover:shadow-[--shadow-md] transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="size-12 rounded-[--radius-lg] bg-[--teal-100] flex items-center justify-center">
                    <MessageSquare className="size-6 text-[--teal-700]" />
                  </div>
                  <div>
                    <h3 className="font-[--font-weight-semibold] text-[--foreground]">Start Chat</h3>
                    <p className="text-sm text-[--muted-foreground]">Get AI support</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-[--shadow-md] transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="size-12 rounded-[--radius-lg] bg-[--sage-100] flex items-center justify-center">
                    <Users className="size-6 text-[--sage-700]" />
                  </div>
                  <div>
                    <h3 className="font-[--font-weight-semibold] text-[--foreground]">Find Specialist</h3>
                    <p className="text-sm text-[--muted-foreground]">Browse providers</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-[--shadow-md] transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="size-12 rounded-[--radius-lg] bg-[--amber-100] flex items-center justify-center">
                    <Calendar className="size-6 text-[--amber-700]" />
                  </div>
                  <div>
                    <h3 className="font-[--font-weight-semibold] text-[--foreground]">Book Session</h3>
                    <p className="text-sm text-[--muted-foreground]">Schedule appointment</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-[--shadow-md] transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="size-12 rounded-[--radius-lg] bg-[--sand-200] flex items-center justify-center">
                    <FileText className="size-6 text-[--sand-700]" />
                  </div>
                  <div>
                    <h3 className="font-[--font-weight-semibold] text-[--foreground]">View Reports</h3>
                    <p className="text-sm text-[--muted-foreground]">Track progress</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Left Column */}
            <div className="md:col-span-2 space-y-6">
              {/* Next Appointment */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Next Appointment</CardTitle>
                    <Badge variant="confirmed">Confirmed</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-start gap-4">
                    <Avatar src="" fallback="DR" size="lg" />
                    <div className="flex-1">
                      <h3 className="font-[--font-weight-semibold] text-[--foreground]">
                        Dr. Michael Rodriguez
                      </h3>
                      <p className="text-sm text-[--muted-foreground] mb-3">
                        Clinical Psychologist • Cognitive Behavioral Therapy
                      </p>
                      <div className="flex items-center gap-4 text-sm text-[--foreground]">
                        <div className="flex items-center gap-2">
                          <Calendar className="size-4 text-[--muted-foreground]" />
                          <span>Tomorrow, May 13</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="size-4 text-[--muted-foreground]" />
                          <span>2:00 PM - 3:00 PM</span>
                        </div>
                      </div>
                    </div>
                    <Button variant="secondary" size="sm">View Details</Button>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Your recent sessions and interactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3 pb-4 border-b border-[--border]">
                      <div className="size-10 rounded-full bg-[--teal-100] flex items-center justify-center flex-shrink-0">
                        <MessageSquare className="size-5 text-[--teal-700]" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                          AI Chat Session
                        </p>
                        <p className="text-sm text-[--muted-foreground]">
                          Discussed coping strategies for work stress
                        </p>
                        <p className="text-xs text-[--muted-foreground] mt-1">2 hours ago</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 pb-4 border-b border-[--border]">
                      <div className="size-10 rounded-full bg-[--sage-100] flex items-center justify-center flex-shrink-0">
                        <Calendar className="size-5 text-[--sage-700]" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                          Appointment Completed
                        </p>
                        <p className="text-sm text-[--muted-foreground]">
                          Session with Dr. Rodriguez
                        </p>
                        <p className="text-xs text-[--muted-foreground] mt-1">May 6, 2026</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="size-10 rounded-full bg-[--sand-200] flex items-center justify-center flex-shrink-0">
                        <FileText className="size-5 text-[--sand-700]" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                          Weekly Report Generated
                        </p>
                        <p className="text-sm text-[--muted-foreground]">
                          Your mental health summary is ready
                        </p>
                        <p className="text-xs text-[--muted-foreground] mt-1">May 5, 2026</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Current Risk State */}
              <Card>
                <CardHeader>
                  <CardTitle>Current Risk State</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-4">
                    <Badge variant="risk-low" className="text-base px-4 py-2">Low Risk</Badge>
                    <p className="text-sm text-[--muted-foreground] mt-4">
                      Based on your recent activity and mood tracking, you're doing well. Keep up the good work!
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Latest Mood Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>This Week's Mood</CardTitle>
                  <CardDescription>Average mood rating</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-4">
                    <div className="text-4xl font-[--font-weight-semibold] text-[--teal-700] mb-2">
                      7.2
                    </div>
                    <p className="text-sm text-[--muted-foreground]">out of 10</p>
                    <div className="flex items-center justify-center gap-2 mt-4 text-sm text-[--success]">
                      <TrendingUp className="size-4" />
                      <span>+0.8 from last week</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Unread Notifications */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Notifications</CardTitle>
                    <Badge variant="default">3 New</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 rounded-[--radius-lg] bg-[--teal-50] border border-[--teal-200]">
                      <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                        Appointment Reminder
                      </p>
                      <p className="text-xs text-[--muted-foreground] mt-1">
                        Tomorrow at 2:00 PM
                      </p>
                    </div>

                    <div className="p-3 rounded-[--radius-lg] bg-[--sand-100] border border-[--sand-300]">
                      <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                        New Message
                      </p>
                      <p className="text-xs text-[--muted-foreground] mt-1">
                        From Dr. Rodriguez
                      </p>
                    </div>

                    <div className="p-3 rounded-[--radius-lg] bg-[--sage-100] border border-[--sage-300]">
                      <p className="text-sm font-[--font-weight-medium] text-[--foreground]">
                        Report Ready
                      </p>
                      <p className="text-xs text-[--muted-foreground] mt-1">
                        Weekly summary available
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" className="w-full mt-4" size="sm">
                    View All
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
