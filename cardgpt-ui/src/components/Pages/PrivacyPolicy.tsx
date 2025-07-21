import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Eye, Database, Lock } from 'lucide-react';

const PrivacyPolicy: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Home</span>
            </button>
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Privacy Policy</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          
          <div className="mb-8">
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Last updated: {new Date().toLocaleDateString('en-IN')}
            </p>
          </div>

          <div className="prose dark:prose-invert max-w-none">
            
            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-4">
                <Eye className="h-6 w-6 text-blue-600" />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Information We Collect</h2>
              </div>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  CardGPT collects minimal information to provide you with the best credit card assistance experience:
                </p>
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Chat Queries:</strong> Your questions and interactions with our AI assistant to provide accurate responses</li>
                  <li><strong>Authentication Data:</strong> When you sign in with Google, we collect your email, name, and profile picture</li>
                  <li><strong>Usage Analytics:</strong> Query counts and session information to manage free tier limits</li>
                  <li><strong>Technical Data:</strong> Device information, browser type, and IP address for security and performance</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-4">
                <Database className="h-6 w-6 text-green-600" />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">How We Use Your Information</h2>
              </div>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  Your information is used solely to provide and improve our credit card assistance service:
                </p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Process and respond to your credit card queries using AI/ML models</li>
                  <li>Manage user authentication and session security</li>
                  <li>Enforce usage limits for free tier users (5 queries per day)</li>
                  <li>Improve our AI models and service quality</li>
                  <li>Provide customer support when needed</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-4">
                <Lock className="h-6 w-6 text-purple-600" />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Data Protection & Security</h2>
              </div>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  We implement industry-standard security measures to protect your information:
                </p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>All data is encrypted in transit using HTTPS/TLS</li>
                  <li>Secure authentication via Google OAuth 2.0</li>
                  <li>JWT tokens for secure session management</li>
                  <li>Regular security audits and updates</li>
                  <li>No storage of sensitive financial information</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Third-Party Services</h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>CardGPT integrates with the following trusted third-party services:</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Google OAuth:</strong> For secure user authentication</li>
                  <li><strong>Google Vertex AI:</strong> For AI-powered search and responses</li>
                  <li><strong>Google Gemini:</strong> For natural language processing</li>
                  <li><strong>Vercel:</strong> For frontend hosting and analytics</li>
                  <li><strong>Railway:</strong> For backend API hosting</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Data Retention</h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <ul className="list-disc pl-6 space-y-2">
                  <li>Chat queries are stored temporarily for service improvement</li>
                  <li>User account data is retained while your account is active</li>
                  <li>Analytics data is aggregated and anonymized after 90 days</li>
                  <li>You can request data deletion by contacting us</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Your Rights</h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>You have the following rights regarding your personal data:</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Access your personal data and download a copy</li>
                  <li>Correct any inaccurate personal data</li>
                  <li>Request deletion of your personal data</li>
                  <li>Object to processing of your personal data</li>
                  <li>Withdraw consent for data processing</li>
                </ul>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Contact Us</h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  If you have any questions about this Privacy Policy or how we handle your data, please contact us:
                </p>
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <p><strong>Email:</strong> Not available (Development phase)</p>
                  <p><strong>Twitter:</strong> @maharajamandy or @jockaayush</p>
                  <p><strong>GitHub:</strong> Available in our repository</p>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 dark:border-gray-600 pt-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Updates to This Policy</h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date.
                </p>
                <p>
                  By continuing to use CardGPT after any changes to this Privacy Policy, you accept the updated terms.
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;