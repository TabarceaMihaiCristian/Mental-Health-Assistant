import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Textarea } from "../components/ui/Textarea";
import { Select } from "../components/ui/Select";
import { Badge } from "../components/ui/Badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { Avatar } from "../components/ui/Avatar";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner, LoadingSkeleton } from "../components/ui/LoadingSpinner";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/Tabs";
import { Calendar, AlertCircle, CheckCircle, XCircle, Info } from "lucide-react";

export default function DesignSystem() {
  return (
    <div className="min-h-screen bg-[--background] p-8">
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Header */}
        <div className="border-b border-[--border] pb-8">
          <h1 className="text-4xl font-[--font-weight-semibold] text-[--foreground] mb-2">
            Mental Health Assistant Design System
          </h1>
          <p className="text-[--muted-foreground] max-w-3xl">
            A comprehensive design system for a serious, premium, calm healthcare-tech product.
            Built with deep teal, muted slate, warm sand, and soft sage tones.
          </p>
        </div>

        {/* Color System */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Color System</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Primary - Deep Teal</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--teal-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Neutral - Muted Slate</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--slate-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Accent - Warm Sand</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--sand-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Success - Soft Sage</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--sage-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Danger - Alert Red</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--red-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Warning - Amber</h3>
              <div className="grid grid-cols-10 gap-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((weight) => (
                  <div key={weight} className="space-y-2">
                    <div
                      className="h-16 rounded-[--radius-lg] border border-[--border]"
                      style={{ backgroundColor: `var(--amber-${weight})` }}
                    />
                    <p className="text-xs text-center text-[--muted-foreground]">{weight}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Typography */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Typography</h2>
          <div className="space-y-4 border border-[--border] rounded-[--radius-xl] p-6">
            <div>
              <h1 className="text-[--foreground]">Heading 1 - The quick brown fox</h1>
              <p className="text-xs text-[--muted-foreground] mt-1">2xl / Medium / 1.5 line-height</p>
            </div>
            <div>
              <h2 className="text-[--foreground]">Heading 2 - The quick brown fox</h2>
              <p className="text-xs text-[--muted-foreground] mt-1">xl / Medium / 1.5 line-height</p>
            </div>
            <div>
              <h3 className="text-[--foreground]">Heading 3 - The quick brown fox</h3>
              <p className="text-xs text-[--muted-foreground] mt-1">lg / Medium / 1.5 line-height</p>
            </div>
            <div>
              <h4 className="text-[--foreground]">Heading 4 - The quick brown fox</h4>
              <p className="text-xs text-[--muted-foreground] mt-1">base / Medium / 1.5 line-height</p>
            </div>
            <div>
              <p className="text-[--foreground]">Body text - The quick brown fox jumps over the lazy dog. This is how regular paragraph text appears throughout the application.</p>
              <p className="text-xs text-[--muted-foreground] mt-1">base / Normal / 1.5 line-height</p>
            </div>
            <div>
              <p className="text-sm text-[--muted-foreground]">Small text - Supporting information and secondary content</p>
              <p className="text-xs text-[--muted-foreground] mt-1">sm / Normal</p>
            </div>
          </div>
        </section>

        {/* Buttons */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Buttons</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Variants</h3>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="success">Success</Button>
                <Button variant="primary" disabled>Disabled</Button>
                <Button variant="primary" loading>Loading</Button>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Sizes</h3>
              <div className="flex items-center flex-wrap gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>
          </div>
        </section>

        {/* Inputs */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Form Inputs</h2>
          <div className="grid grid-cols-2 gap-6">
            <Input label="Text Input" placeholder="Enter text..." />
            <Input type="email" label="Email Input" placeholder="email@example.com" />
            <Input type="password" label="Password Input" placeholder="••••••••" />
            <Input label="With Error" placeholder="Invalid input" error="This field is required" />
            <Select
              label="Select Input"
              options={[
                { value: "", label: "Select an option..." },
                { value: "1", label: "Option 1" },
                { value: "2", label: "Option 2" },
              ]}
            />
            <Input type="date" label="Date Input" />
          </div>
          <div className="mt-6">
            <Textarea label="Textarea" placeholder="Enter multiple lines of text..." />
          </div>
        </section>

        {/* Badges */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Badges</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Appointment Status</h3>
              <div className="flex flex-wrap gap-3">
                <Badge variant="requested">Requested</Badge>
                <Badge variant="confirmed">Confirmed</Badge>
                <Badge variant="completed">Completed</Badge>
                <Badge variant="cancelled">Cancelled</Badge>
                <Badge variant="rejected">Rejected</Badge>
                <Badge variant="rescheduled">Rescheduled</Badge>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-[--font-weight-medium] text-[--foreground] mb-3">Risk Levels</h3>
              <div className="flex flex-wrap gap-3">
                <Badge variant="risk-low">Low Risk</Badge>
                <Badge variant="risk-medium">Medium Risk</Badge>
                <Badge variant="risk-high">High Risk</Badge>
                <Badge variant="risk-critical">Critical Risk</Badge>
              </div>
            </div>
          </div>
        </section>

        {/* Cards */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Cards</h2>
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Card Title</CardTitle>
                <CardDescription>This is a supporting description for the card content.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-[--foreground]">Card content goes here. This is the main area for displaying information.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Simple Card</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[--muted-foreground]">Cards can have varying levels of complexity based on the use case.</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Avatars */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Avatars</h2>
          <div className="flex items-center gap-4">
            <Avatar fallback="JD" size="sm" />
            <Avatar fallback="AS" size="md" />
            <Avatar fallback="MH" size="lg" />
            <Avatar fallback="SK" size="xl" />
          </div>
        </section>

        {/* Tabs */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Tabs</h2>
          <Tabs defaultValue="tab1">
            <TabsList>
              <TabsTrigger value="tab1">Tab 1</TabsTrigger>
              <TabsTrigger value="tab2">Tab 2</TabsTrigger>
              <TabsTrigger value="tab3">Tab 3</TabsTrigger>
            </TabsList>
            <TabsContent value="tab1">
              <Card>
                <CardContent className="pt-6">
                  Content for Tab 1
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="tab2">
              <Card>
                <CardContent className="pt-6">
                  Content for Tab 2
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="tab3">
              <Card>
                <CardContent className="pt-6">
                  Content for Tab 3
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>

        {/* States */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">States</h2>
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Empty State</CardTitle>
              </CardHeader>
              <CardContent>
                <EmptyState
                  icon={<Calendar className="size-12" />}
                  title="No appointments yet"
                  description="You don't have any upcoming appointments. Book your first session to get started."
                  action={<Button>Book Appointment</Button>}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Loading State</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <LoadingSpinner size="md" />
                  <div className="space-y-2">
                    <LoadingSkeleton className="h-4 w-full" />
                    <LoadingSkeleton className="h-4 w-3/4" />
                    <LoadingSkeleton className="h-4 w-1/2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Alerts */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Alert States</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 rounded-[--radius-lg] bg-[--success-light] border border-[--success]">
              <CheckCircle className="size-5 text-[--success] mt-0.5" />
              <div>
                <h4 className="font-[--font-weight-medium] text-[--success]">Success</h4>
                <p className="text-sm text-[--foreground] mt-1">Your appointment has been confirmed successfully.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-[--radius-lg] bg-[--info-light] border border-[--info]">
              <Info className="size-5 text-[--info] mt-0.5" />
              <div>
                <h4 className="font-[--font-weight-medium] text-[--info]">Information</h4>
                <p className="text-sm text-[--foreground] mt-1">Your next appointment is scheduled for tomorrow at 2:00 PM.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-[--radius-lg] bg-[--warning-light] border border-[--warning]">
              <AlertCircle className="size-5 text-[--warning] mt-0.5" />
              <div>
                <h4 className="font-[--font-weight-medium] text-[--warning]">Warning</h4>
                <p className="text-sm text-[--foreground] mt-1">Please complete your profile to access all features.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-[--radius-lg] bg-[--red-100] border border-[--destructive]">
              <XCircle className="size-5 text-[--destructive] mt-0.5" />
              <div>
                <h4 className="font-[--font-weight-medium] text-[--destructive]">Error</h4>
                <p className="text-sm text-[--foreground] mt-1">There was a problem processing your request. Please try again.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Spacing Scale */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Spacing Scale</h2>
          <div className="space-y-2">
            {[1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24].map((size) => (
              <div key={size} className="flex items-center gap-4">
                <div className="w-16 text-sm text-[--muted-foreground]">--space-{size}</div>
                <div
                  className="h-6 bg-[--primary] rounded"
                  style={{ width: `var(--space-${size})` }}
                />
              </div>
            ))}
          </div>
        </section>

        {/* Shadow Scale */}
        <section>
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-6">Shadow Scale</h2>
          <div className="grid grid-cols-4 gap-6">
            <div className="p-6 rounded-[--radius-lg] bg-[--card] border border-[--border]" style={{ boxShadow: "var(--shadow-sm)" }}>
              <p className="text-sm text-[--muted-foreground]">Shadow SM</p>
            </div>
            <div className="p-6 rounded-[--radius-lg] bg-[--card] border border-[--border]" style={{ boxShadow: "var(--shadow-md)" }}>
              <p className="text-sm text-[--muted-foreground]">Shadow MD</p>
            </div>
            <div className="p-6 rounded-[--radius-lg] bg-[--card] border border-[--border]" style={{ boxShadow: "var(--shadow-lg)" }}>
              <p className="text-sm text-[--muted-foreground]">Shadow LG</p>
            </div>
            <div className="p-6 rounded-[--radius-lg] bg-[--card] border border-[--border]" style={{ boxShadow: "var(--shadow-xl)" }}>
              <p className="text-sm text-[--muted-foreground]">Shadow XL</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
