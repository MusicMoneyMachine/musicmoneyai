import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AboutPage() {
  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">About Our Platform</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          A modern web application built with Next.js 15 on the frontend and Python FastAPI on the backend.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        <Card>
          <CardHeader>
            <CardTitle>Frontend Technologies</CardTitle>
            <CardDescription>Built with the latest web technologies</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>Next.js 15</strong> - React framework with App Router</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>TypeScript</strong> - For type safety and better developer experience</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>Tailwind CSS</strong> - Utility-first CSS framework</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>Shadcn/UI</strong> - Reusable UI components</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>NextAuth.js</strong> - Authentication for Next.js</span>
              </li>
            </ul>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Backend Technologies</CardTitle>
            <CardDescription>Powered by Python and PostgreSQL</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>Python FastAPI</strong> - Modern, fast web framework</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>PostgreSQL</strong> - Powerful, open source object-relational database</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>SQLAlchemy</strong> - SQL toolkit and ORM for Python</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>Pydantic</strong> - Data validation and settings management</span>
              </li>
              <li className="flex items-center">
                <span className="inline-flex items-center justify-center w-6 h-6 mr-2 text-sm font-semibold rounded-full bg-primary text-primary-foreground">•</span>
                <span><strong>JWT Authentication</strong> - Secure token-based authentication</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
      
      <h2 className="text-3xl font-bold text-center mb-8">Our Team</h2>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
        {[
          {
            name: "Alex Johnson",
            role: "Frontend Developer",
            bio: "Specializes in React and Next.js development with 5+ years of experience."
          },
          {
            name: "Sam Taylor",
            role: "Backend Developer",
            bio: "Python expert focusing on API development and database optimization."
          },
          {
            name: "Jamie Smith",
            role: "UI/UX Designer",
            bio: "Creates beautiful, intuitive interfaces with a focus on user experience."
          }
        ].map((member, index) => (
          <Card key={index} className="overflow-hidden">
            <div className="bg-gradient-to-r from-primary/10 to-secondary/10 h-32 flex items-center justify-center">
              <div className="h-20 w-20 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-2xl font-bold text-primary">{member.name.charAt(0)}</span>
              </div>
            </div>
            <CardHeader>
              <CardTitle>{member.name}</CardTitle>
              <CardDescription>{member.role}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{member.bio}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <Card className="mb-16">
        <CardHeader>
          <CardTitle className="text-center">Our Mission</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-lg text-muted-foreground max-w-3xl mx-auto">
            We're committed to creating high-quality, scalable web applications that help businesses grow and succeed. Our platform combines the best of modern frontend and backend technologies to deliver exceptional user experiences.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}