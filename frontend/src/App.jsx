import { useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  Clock3,
  FileText,
  Search,
  ShieldCheck,
  UploadCloud,
  X,
  XCircle,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";


// ============================================================
// DEMO DOCUMENTS
// ============================================================

const initialDocuments = [
  {
    id: "1",
    name: "aadhaar_demo.pdf",
    type: "Aadhaar",
    status: "validated",
    uploadedAt: "24 Sep 2026, 10:42 AM",
    size: 1.24,

    fields: [
      {
        label: "Full Name",
        value: "AARAV DEMO KUMAR",
        confidence: 98,
        status: "pass",
      },
      {
        label: "Date of Birth",
        value: "01/01/1998",
        confidence: 97,
        status: "pass",
      },
      {
        label: "Address",
        value:
          "123 DEMO STREET, TEST NAGAR, NEW DELHI",
        confidence: 93,
        status: "pass",
      },
    ],

    validations: [
      {
        label: "Document readable",
        status: "pass",
        reason:
          "OCR successfully extracted the document.",
      },
      {
        label: "Name consistency",
        status: "pass",
        reason:
          "Name matches the submitted PAN.",
      },
      {
        label: "Date of birth consistency",
        status: "pass",
        reason:
          "Date of birth matches the submitted PAN.",
      },
    ],
  },

  {
    id: "2",
    name: "pan_demo.pdf",
    type: "PAN",
    status: "flagged",
    uploadedAt: "24 Sep 2026, 10:44 AM",
    size: 0.89,

    fields: [
      {
        label: "Full Name",
        value: "RAJESH DEMO KUMAR",
        confidence: 98,
        status: "flag",
        reason:
          "Name differs from Aadhaar.",
      },
      {
        label: "PAN Number",
        value: "DEMOX1234Z",
        confidence: 99,
        status: "pass",
      },
      {
        label: "Date of Birth",
        value: "01/01/1998",
        confidence: 97,
        status: "pass",
      },
    ],

    validations: [
      {
        label: "Document readable",
        status: "pass",
        reason:
          "OCR successfully extracted the document.",
      },
      {
        label: "PAN format",
        status: "pass",
        reason:
          "PAN matches the expected format.",
      },
      {
        label: "Name consistency",
        status: "flag",
        reason:
          "PAN name does not match Aadhaar.",
      },
    ],
  },

  {
    id: "3",
    name: "bank_statement_demo.pdf",
    type: "Bank Statement",
    status: "pending",
    uploadedAt: "24 Sep 2026, 10:46 AM",
    size: 2.45,

    fields: [],
    validations: [],
  },
];


// ============================================================
// STATUS BADGE
// ============================================================

function StatusBadge({ status }) {
  const config = {
    validated: {
      label: "Validated",
      icon: CheckCircle2,
      className:
        "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300",
    },

    flagged: {
      label: "Flagged",
      icon: AlertCircle,
      className:
        "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300",
    },

    rejected: {
      label: "Rejected",
      icon: XCircle,
      className:
        "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300",
    },

    pending: {
      label: "Pending",
      icon: Clock3,
      className:
        "border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300",
    },
  };

  const current =
    config[status] || config.pending;

  const Icon = current.icon;

  return (
    <Badge
      variant="outline"
      className={`gap-1.5 px-2.5 py-1 font-medium ${current.className}`}
    >
      <Icon className="h-3.5 w-3.5" />

      {current.label}
    </Badge>
  );
}


// ============================================================
// VALIDATION ICON
// ============================================================

function ValidationIcon({ status }) {
  if (status === "pass") {
    return (
      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-950/40">
        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
      </div>
    );
  }

  if (status === "fail") {
    return (
      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-red-50 dark:bg-red-950/40">
        <XCircle className="h-4 w-4 text-red-600" />
      </div>
    );
  }

  return (
    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-50 dark:bg-amber-950/40">
      <AlertCircle className="h-4 w-4 text-amber-600" />
    </div>
  );
}


// ============================================================
// SUMMARY CARD
// ============================================================

function SummaryCard({
  label,
  value,
  description,
  icon: Icon,
}) {
  return (
    <Card className="border-slate-200 shadow-sm dark:border-slate-800">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">

          <div>
            <p className="text-xs font-medium text-slate-500">
              {label}
            </p>

            <p className="mt-2 text-2xl font-semibold tracking-tight">
              {value}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {description}
            </p>
          </div>

          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-900">
            <Icon className="h-4 w-4 text-slate-500" />
          </div>

        </div>
      </CardContent>
    </Card>
  );
}


// ============================================================
// MAIN APP
// ============================================================

function App() {

  const [documents, setDocuments] =
    useState(initialDocuments);

  const [selectedDocument, setSelectedDocument] =
    useState(null);

  const [uploadedFiles, setUploadedFiles] =
    useState([]);

  const [verifying, setVerifying] =
    useState(false);

  const [backendError, setBackendError] =
    useState("");

  const [verificationResult, setVerificationResult] =
    useState(null);

  const [search, setSearch] =
    useState("");

  const [filter, setFilter] =
    useState("all");

  const [dragging, setDragging] =
    useState(false);

  const fileInputRef =
    useRef(null);


  // ==========================================================
  // FILTER DOCUMENTS
  // ==========================================================

  const filteredDocuments = useMemo(() => {

    return documents.filter((document) => {

      const matchesSearch =
        document.name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        document.type
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesFilter =
        filter === "all" ||
        document.status === filter;

      return (
        matchesSearch &&
        matchesFilter
      );
    });

  }, [documents, search, filter]);


  // ==========================================================
  // HANDLE FILES
  // ==========================================================

  const handleFiles = (files) => {

    if (!files || files.length === 0) {
      return;
    }

    const allowedTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
    ];

    const validFiles = [];
    const invalidFiles = [];

    Array.from(files).forEach((file) => {

      if (!allowedTypes.includes(file.type)) {

        invalidFiles.push(
          `${file.name}: unsupported file type`
        );

        return;
      }

      if (
        file.size >
        10 * 1024 * 1024
      ) {

        invalidFiles.push(
          `${file.name}: file is larger than 10 MB`
        );

        return;
      }

      validFiles.push(file);
    });


    if (invalidFiles.length > 0) {

      setBackendError(
        invalidFiles.join(" | ")
      );

    } else {

      setBackendError("");
    }


    if (validFiles.length === 0) {
      return;
    }


    // Store actual browser File objects

    setUploadedFiles((current) => [
      ...current,
      ...validFiles,
    ]);


    // Create queue entries

    const newDocuments =
      validFiles.map((file) => ({

        id: crypto.randomUUID(),

        name: file.name,

        type: "Document",

        status: "pending",

        uploadedAt:
          new Date().toLocaleString(),

        size: Number(
          (
            file.size /
            1024 /
            1024
          ).toFixed(2)
        ),

        progress: 0,

        fields: [],

        validations: [],
      }));


    setDocuments((current) => [
      ...newDocuments,
      ...current,
    ]);
  };


  // ==========================================================
  // DRAG AND DROP
  // ==========================================================

  const handleDrop = (event) => {

    event.preventDefault();

    setDragging(false);

    handleFiles(
      event.dataTransfer.files
    );
  };


  // ==========================================================
  // VERIFY DOCUMENTS
  // ==========================================================

  const handleVerifyDocuments =
    async () => {

      const aadhaarFile =
        uploadedFiles.find((file) => {

          const name =
            file.name.toLowerCase();

          return (
            name.includes("aadhaar") ||
            name.includes("aadhar")
          );
        });


      const panFile =
        uploadedFiles.find((file) =>
          file.name
            .toLowerCase()
            .includes("pan")
        );


      const bankFile =
        uploadedFiles.find((file) => {

          const name =
            file.name.toLowerCase();

          return (
            name.includes("bank") ||
            name.includes("statement")
          );
        });


      if (
        !aadhaarFile ||
        !panFile ||
        !bankFile
      ) {

        setBackendError(
          "Please upload Aadhaar, PAN and Bank Statement documents."
        );

        return;
      }


      setBackendError("");

      setVerifying(true);


      try {

        const formData =
          new FormData();

        formData.append(
          "aadhaar",
          aadhaarFile
        );

        formData.append(
          "pan",
          panFile
        );

        formData.append(
          "bank_statement",
          bankFile
        );


        const response =
          await fetch(
            "http://127.0.0.1:8000/validate-documents",
            {
              method: "POST",
              body: formData,
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.detail ||
              "Document verification failed."
          );
        }


        console.log(
          "Backend verification response:",
          data
        );


        const verificationStatus =
          data.agent_decision
            ?.verification_status;

        setVerificationResult(
          data.agent_decision || null
        );


        const newStatus =
          verificationStatus ===
          "VERIFIED"
            ? "validated"
            : "flagged";


        setDocuments((current) =>
          current.map((document) => {

            const documentKey =
              document.name === aadhaarFile.name
                ? "aadhaar"
                : document.name === panFile.name
                  ? "pan"
                  : document.name === bankFile.name
                    ? "bank_statement"
                    : null;

            const verificationDocument =
              documentKey
                ? data.documents?.[documentKey]
                : null;

            const documentLabel =
              documentKey === "aadhaar"
                ? "Aadhaar"
                : documentKey === "pan"
                  ? "PAN"
                  : "Bank Statement";

            const extractedFields = verificationDocument
              ? Object.entries(verificationDocument)
                  .filter(
                    ([key, value]) =>
                      key !== "integrity" &&
                      value !== null &&
                      value !== undefined &&
                      value !== ""
                  )
                  .map(([key, value]) => ({
                    label: key
                      .replaceAll("_", " ")
                      .replace(/\b\w/g, (letter) => letter.toUpperCase()),
                    value: Array.isArray(value)
                      ? `${value.length} item(s)`
                      : String(value),
                    confidence: null,
                    status: "pass",
                  }))
              : document.fields;

            const validationChecks =
              data.validation_results?.checks
                ?.filter((check) =>
                  check.check.startsWith(`${documentLabel}:`)
                )
                .map((check) => ({
                  label: check.check.replace(`${documentLabel}: `, ""),
                  status:
                    check.status === "PASS"
                      ? "pass"
                      : "flag",
                  reason: check.message,
                })) || document.validations;

            const isUploadedDocument =
              document.name ===
                aadhaarFile.name ||
              document.name ===
                panFile.name ||
              document.name ===
                bankFile.name;


            if (
              !isUploadedDocument
            ) {
              return document;
            }


            return {
              ...document,

              type: documentLabel,

              status: newStatus,

              progress: 100,

              fields: extractedFields,

              validations: validationChecks,
            };
          })
        );


        setBackendError("");


        alert(
          `Verification completed: ${verificationStatus}`
        );

      } catch (error) {

        console.error(
          "Verification error:",
          error
        );

        setBackendError(
          error.message ||
            "Unable to verify documents."
        );

      } finally {

        setVerifying(false);
      }
    };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="sticky top-0 z-30 border-b bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">

        <div className="flex h-16 items-center justify-between px-6">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900">

              <ShieldCheck className="h-5 w-5" />

            </div>

            <div>

              <p className="text-sm font-semibold tracking-tight">
                VerifyFlow
              </p>

              <p className="text-[11px] text-slate-500">
                NBFC Compliance
              </p>

            </div>

          </div>


          <div className="flex items-center gap-3">

            <div className="hidden text-right sm:block">

              <p className="text-sm font-medium">
                Priya Kumari
              </p>

              <p className="text-xs text-slate-500">
                Compliance Reviewer
              </p>

            </div>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
              PK
            </div>

          </div>

        </div>

      </header>


      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="mx-auto max-w-[1400px] space-y-6 p-6">

        {/* PAGE HEADER */}

        <section className="flex flex-col justify-between gap-4 md:flex-row md:items-end">

          <div>

            <p className="text-sm font-medium text-slate-500">
              Compliance workspace
            </p>

            <h1 className="mt-1 text-2xl font-semibold tracking-tight">
              Document verification
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Upload and review KYC documents,
              extracted fields, and automated
              validation results.
            </p>

          </div>


          <Button
            className="gap-2"
            onClick={(event) => {

              event.stopPropagation();

              fileInputRef.current?.click();

            }}
          >

            <UploadCloud className="h-4 w-4" />

            Upload documents

          </Button>

        </section>


        {/* SUMMARY CARDS */}

        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">

          <SummaryCard
            label="Total documents"
            value={documents.length}
            description="In review queue"
            icon={FileText}
          />

          <SummaryCard
            label="Validated"
            value={
              documents.filter(
                (document) =>
                  document.status ===
                  "validated"
              ).length
            }
            description="Checks passed"
            icon={CheckCircle2}
          />

          <SummaryCard
            label="Flagged"
            value={
              documents.filter(
                (document) =>
                  document.status ===
                  "flagged"
              ).length
            }
            description="Needs review"
            icon={AlertCircle}
          />

          <SummaryCard
            label="Pending"
            value={
              documents.filter(
                (document) =>
                  document.status ===
                  "pending"
              ).length
            }
            description="Processing"
            icon={Clock3}
          />

        </section>


        {/* ===================================================
            UPLOAD ZONE
        ==================================================== */}

        <section
          onDragOver={(event) => {

            event.preventDefault();

            setDragging(true);

          }}

          onDragLeave={() =>
            setDragging(false)
          }

          onDrop={handleDrop}

          onClick={() =>
            fileInputRef.current?.click()
          }

          className={`cursor-pointer rounded-xl border border-dashed p-8 transition-all ${
            dragging
              ? "border-slate-900 bg-slate-100 shadow-sm dark:border-white dark:bg-slate-900"
              : "border-slate-300 bg-white hover:border-slate-400 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-950 dark:hover:bg-slate-900"
          }`}
        >

          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(event) => {

              handleFiles(
                event.target.files
              );

              event.target.value = "";

            }}
          />


          <div className="mx-auto flex max-w-xl flex-col items-center text-center">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl border bg-slate-50 dark:border-slate-700 dark:bg-slate-900">

              <UploadCloud className="h-5 w-5 text-slate-500" />

            </div>


            <h2 className="mt-4 text-sm font-semibold">

              Drop documents here or click
              to browse

            </h2>


            <p className="mt-1 text-xs text-slate-500">

              PDF, JPG or PNG · Maximum
              file size 10 MB

            </p>

          </div>

        </section>


        {/* ERROR */}

        {backendError && (

          <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">

            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />

            <span>
              {backendError}
            </span>

          </div>

        )}


        {verificationResult && (

          <Card className="border-slate-200 shadow-sm dark:border-slate-800">

            <CardContent className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Agent recommendation
                </p>

                <p className="mt-1 text-lg font-semibold">
                  {verificationResult.verification_status ===
                  "VERIFIED"
                    ? "Documents can be verified"
                    : "Human review required"}
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  {verificationResult.reason}
                </p>

              </div>

              <StatusBadge
                status={
                  verificationResult.verification_status ===
                  "VERIFIED"
                    ? "validated"
                    : "flagged"
                }
              />

            </CardContent>

          </Card>
        )}


        {/* VERIFY BUTTON */}

        <div className="flex justify-end">

          <Button
            onClick={handleVerifyDocuments}
            disabled={
              verifying ||
              uploadedFiles.length === 0
            }
            className="gap-2"
          >

            {verifying ? (
              <>

                <Clock3 className="h-4 w-4 animate-spin" />

                Verifying documents...

              </>
            ) : (
              <>

                <ShieldCheck className="h-4 w-4" />

                Verify documents

              </>
            )}

          </Button>

        </div>


        {/* ===================================================
            DOCUMENT QUEUE
        ==================================================== */}

        <Card className="overflow-hidden border-slate-200 shadow-sm dark:border-slate-800">

          <CardHeader className="border-b px-5 py-4 dark:border-slate-800">

            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

              <div>

                <CardTitle className="text-base">
                  Document queue
                </CardTitle>

                <p className="mt-1 text-xs text-slate-500">

                  {filteredDocuments.length}
                  {" "}
                  documents in review queue

                </p>

              </div>


              <div className="flex flex-col gap-2 sm:flex-row">

                <div className="relative">

                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />

                  <Input
                    value={search}
                    onChange={(event) =>
                      setSearch(
                        event.target.value
                      )
                    }
                    placeholder="Search documents..."
                    className="w-full pl-9 sm:w-64"
                  />

                </div>


                <div className="relative">

                  <select
                    value={filter}
                    onChange={(event) =>
                      setFilter(
                        event.target.value
                      )
                    }
                    className="h-9 w-full appearance-none rounded-md border border-slate-200 bg-white px-3 pr-9 text-sm outline-none focus:ring-2 focus:ring-slate-400 dark:border-slate-800 dark:bg-slate-950 sm:w-40"
                  >

                    <option value="all">
                      All statuses
                    </option>

                    <option value="validated">
                      Validated
                    </option>

                    <option value="flagged">
                      Flagged
                    </option>

                    <option value="pending">
                      Pending
                    </option>

                    <option value="rejected">
                      Rejected
                    </option>

                  </select>


                  <ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-4 w-4 text-slate-400" />

                </div>

              </div>

            </div>

          </CardHeader>


          <CardContent className="p-0">

            {filteredDocuments.length === 0 ? (

              <EmptyState />

            ) : (

              <div className="overflow-x-auto">

                <Table>

                  <TableHeader className="bg-slate-50 dark:bg-slate-900">

                    <TableRow>

                      <TableHead className="min-w-[280px]">
                        Document
                      </TableHead>

                      <TableHead>
                        Type
                      </TableHead>

                      <TableHead>
                        Status
                      </TableHead>

                      <TableHead>
                        Uploaded
                      </TableHead>

                      <TableHead>
                        Size
                      </TableHead>

                      <TableHead className="text-right">
                        Action
                      </TableHead>

                    </TableRow>

                  </TableHeader>


                  <TableBody>

                    {filteredDocuments.map(
                      (document) => (

                        <TableRow
                          key={document.id}
                          className="cursor-pointer transition-colors hover:bg-slate-50 dark:hover:bg-slate-900"
                          onClick={() =>
                            setSelectedDocument(
                              document
                            )
                          }
                        >

                          <TableCell>

                            <div className="flex items-center gap-3">

                              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border bg-white dark:border-slate-700 dark:bg-slate-950">

                                <FileText className="h-4 w-4 text-slate-500" />

                              </div>


                              <div className="min-w-0">

                                <p className="truncate font-medium">
                                  {document.name}
                                </p>


                                {document.progress !==
                                  undefined &&
                                  document.progress <
                                    100 && (

                                    <div className="mt-2 w-36">

                                      <Progress
                                        value={
                                          document.progress
                                        }
                                        className="h-1"
                                      />

                                    </div>

                                  )}

                              </div>

                            </div>

                          </TableCell>


                          <TableCell className="text-slate-600 dark:text-slate-400">

                            {document.type}

                          </TableCell>


                          <TableCell>

                            <StatusBadge
                              status={
                                document.status
                              }
                            />

                          </TableCell>


                          <TableCell className="whitespace-nowrap text-sm text-slate-500">

                            {document.uploadedAt}

                          </TableCell>


                          <TableCell className="text-sm text-slate-500">

                            {document.size} MB

                          </TableCell>


                          <TableCell className="text-right">

                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(event) => {

                                event.stopPropagation();

                                setSelectedDocument(
                                  document
                                );

                              }}
                            >

                              Review

                            </Button>

                          </TableCell>

                        </TableRow>

                      )
                    )}

                  </TableBody>

                </Table>

              </div>

            )}

          </CardContent>

        </Card>


        {/* FOOTER */}

        <p className="pb-4 text-center text-xs text-slate-400">

          Automated checks assist compliance review
          and do not establish document authenticity
          or make lending decisions.

        </p>

      </main>


      {/* =====================================================
          DETAIL MODAL
      ====================================================== */}

      {selectedDocument && (

        <DocumentDetail
          document={selectedDocument}
          onClose={() =>
            setSelectedDocument(null)
          }
        />

      )}

    </div>
  );
}


// ============================================================
// EMPTY STATE
// ============================================================

function EmptyState() {

  return (

    <div className="flex min-h-[280px] flex-col items-center justify-center px-6 text-center">

      <div className="flex h-12 w-12 items-center justify-center rounded-xl border bg-slate-50 dark:border-slate-800 dark:bg-slate-900">

        <FileText className="h-5 w-5 text-slate-400" />

      </div>


      <h3 className="mt-4 text-sm font-semibold">
        No documents found
      </h3>


      <p className="mt-1 max-w-sm text-xs text-slate-500">

        Upload KYC documents to start
        the verification process.

      </p>

    </div>

  );
}


// ============================================================
// DOCUMENT DETAIL
// ============================================================

function DocumentDetail({
  document,
  onClose,
}) {

  return (

    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-sm">

      <div className="flex max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-2xl border bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-950">


        {/* MODAL HEADER */}

        <div className="flex items-center justify-between border-b px-6 py-4 dark:border-slate-800">

          <div className="min-w-0">

            <div className="flex flex-wrap items-center gap-3">

              <h2 className="truncate font-semibold">
                {document.name}
              </h2>

              <StatusBadge
                status={document.status}
              />

            </div>


            <p className="mt-1 text-xs text-slate-500">

              {document.type}
              {" · "}
              Uploaded {document.uploadedAt}

            </p>

          </div>


          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
          >

            <X className="h-4 w-4" />

          </Button>

        </div>


        {/* MODAL CONTENT */}

        <div className="grid min-h-0 flex-1 overflow-auto lg:grid-cols-2">


          {/* DOCUMENT PREVIEW */}

          <div className="border-b bg-slate-100 p-6 dark:border-slate-800 dark:bg-slate-900 lg:border-b-0 lg:border-r">

            <div className="mb-3 flex items-center justify-between">

              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Document preview
              </p>

              <Badge variant="outline">
                {document.type}
              </Badge>

            </div>


            <div className="flex min-h-[440px] items-center justify-center rounded-xl border bg-white shadow-sm dark:border-slate-700 dark:bg-slate-950">

              <div className="text-center">

                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-900">

                  <FileText className="h-7 w-7 text-slate-400" />

                </div>


                <p className="mt-4 text-sm font-medium">
                  {document.name}
                </p>


                <p className="mt-1 text-xs text-slate-500">

                  Document preview will appear here

                </p>

              </div>

            </div>

          </div>


          {/* REVIEW DETAILS */}

          <div className="space-y-7 overflow-auto p-6">


            {/* EXTRACTED INFORMATION */}

            <section>

              <div>

                <h3 className="text-sm font-semibold">
                  Extracted information
                </h3>

                <p className="mt-1 text-xs text-slate-500">

                  OCR fields and confidence scores

                </p>

              </div>


              <div className="mt-4 space-y-3">

                {document.fields.length === 0 ? (

                  <div className="rounded-xl border border-dashed p-8 text-center">

                    <Clock3 className="mx-auto h-5 w-5 text-slate-400" />

                    <p className="mt-3 text-sm font-medium">
                      OCR processing
                    </p>

                    <p className="mt-1 text-xs text-slate-500">

                      Extracted fields will appear here.

                    </p>

                  </div>

                ) : (

                  document.fields.map(
                    (field) => (

                      <div
                        key={field.label}
                        className="rounded-xl border p-4 dark:border-slate-800"
                      >

                        <div className="flex items-start justify-between gap-4">

                          <div className="min-w-0">

                            <p className="text-xs font-medium text-slate-500">
                              {field.label}
                            </p>

                            <p className="mt-1 break-words text-sm font-medium">
                              {field.value}
                            </p>

                          </div>


                          <div className="shrink-0 text-right">

                            <p className="text-xs font-semibold">
                              {field.confidence === null
                                ? "n/a"
                                : `${field.confidence}%`}
                            </p>

                            <p className="text-[10px] text-slate-400">
                              confidence
                            </p>

                          </div>

                        </div>


                        {field.reason && (

                          <div className="mt-3 flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-700 dark:bg-amber-950/40 dark:text-amber-300">

                            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />

                            <span>
                              {field.reason}
                            </span>

                          </div>

                        )}

                      </div>

                    )
                  )

                )}

              </div>

            </section>


            {/* VALIDATION RESULTS */}

            <section>

              <div>

                <h3 className="text-sm font-semibold">
                  Validation results
                </h3>

                <p className="mt-1 text-xs text-slate-500">

                  Automated consistency checks

                </p>

              </div>


              <div className="mt-4 divide-y rounded-xl border dark:divide-slate-800 dark:border-slate-800">

                {document.validations.length === 0 ? (

                  <div className="p-8 text-center text-sm text-slate-500">

                    Validation results are
                    not available yet.

                  </div>

                ) : (

                  document.validations.map(
                    (validation) => (

                      <div
                        key={validation.label}
                        className="flex items-start gap-3 p-4"
                      >

                        <ValidationIcon
                          status={
                            validation.status
                          }
                        />


                        <div className="min-w-0 flex-1">

                          <div className="flex flex-col justify-between gap-1 sm:flex-row">

                            <p className="text-sm font-medium">
                              {validation.label}
                            </p>


                            <Badge
                              variant="outline"
                              className={
                                validation.status ===
                                "pass"
                                  ? "w-fit border-emerald-200 text-emerald-700"
                                  : "w-fit border-amber-200 text-amber-700"
                              }
                            >

                              {validation.status ===
                              "pass"
                                ? "PASS"
                                : "FLAGGED"}

                            </Badge>

                          </div>


                          {validation.reason && (

                            <p className="mt-1 text-xs leading-5 text-slate-500">

                              {validation.reason}

                            </p>

                          )}

                        </div>

                      </div>

                    )
                  )

                )}

              </div>

            </section>

          </div>

        </div>

      </div>

    </div>

  );
}


export default App;