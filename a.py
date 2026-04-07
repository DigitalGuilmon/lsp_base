import os

# Definir la ruta del archivo expandiendo el símbolo ~
path = os.path.expanduser(
    "~/dev/lsp_base/spoon-jdt-lsp/src/main/java/com/lsp/spoon/SpoonLanguageServer.java"
)

# El código corregido (sin el import erróneo en la línea 16)
new_code = r"""package com.lsp.spoon;

import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.services.*;
import java.util.concurrent.CompletableFuture;
import java.net.URI;
import java.io.File;
import java.util.*;

// Spoon Imports
import spoon.Launcher;
import spoon.reflect.declaration.*;
import spoon.reflect.code.*;
import spoon.reflect.visitor.filter.TypeFilter;
import spoon.reflect.cu.SourcePosition;

public class SpoonLanguageServer implements LanguageServer, LanguageClientAware {
    private LanguageClient client;

    @Override
    public CompletableFuture<InitializeResult> initialize(InitializeParams params) {
        ServerCapabilities caps = new ServerCapabilities();
        caps.setTextDocumentSync(TextDocumentSyncKind.Full);
        caps.setHoverProvider(true);
        return CompletableFuture.completedFuture(new InitializeResult(caps));
    }

    @Override
    public TextDocumentService getTextDocumentService() {
        return new TextDocumentService() {
            @Override
            public void didOpen(DidOpenTextDocumentParams p) { runAnalysis(p.getTextDocument().getUri()); }
            @Override
            public void didChange(DidChangeTextDocumentParams p) { runAnalysis(p.getTextDocument().getUri()); }
            @Override public void didSave(DidSaveTextDocumentParams p) { runAnalysis(p.getTextDocument().getUri()); }
            @Override public void didClose(DidCloseTextDocumentParams p) {}

            private void runAnalysis(String uri) {
                try {
                    File file = new File(new URI(uri));
                    Launcher spoon = new Launcher();
                    spoon.addInputResource(file.getAbsolutePath());
                    spoon.getEnvironment().setNoClasspath(true);
                    spoon.buildModel();

                    List<Diagnostic> diagnostics = new ArrayList<>();

                    // 1. Análisis de Métodos (Anidación y Longitud/SRP)
                    List<CtMethod<?>> methods = spoon.getModel().getElements(new TypeFilter<>(CtMethod.class));

                    for (CtMethod<?> method : methods) {
                        SourcePosition pos = method.getPosition();
                        if (!pos.isValidPosition()) continue;

                        // REGLA: Métodos demasiado largos (> 50 líneas)
                        int lineCount = pos.getEndLine() - pos.getLine() + 1;
                        if (lineCount > 50) {
                            diagnostics.add(new Diagnostic(
                                createRange(pos, method.getSimpleName().length()),
                                "AVISO SRP: Método muy largo (" + lineCount + " líneas). Considera dividirlo.",
                                DiagnosticSeverity.Warning, "SpoonLinter"
                            ));
                        }

                        // REGLA: Anidación excesiva (Original Aldo)
                        int maxDepth = calculateMaxLoopDepth(method);
                        if (maxDepth > 2 && !hasAuditableAnnotation(method)) {
                            String msg = "Hola Raul y Ajolote!!! de parte de Aldo!!! " +
                                         "CRÍTICO: Método con " + maxDepth + " niveles de anidación sin @Auditable.";
                            diagnostics.add(new Diagnostic(createRange(pos, method.getSimpleName().length() + 10), msg, DiagnosticSeverity.Error, "SpoonLinter"));
                        }
                    }

                    // 2. Análisis de Datos Sensibles (Strings/Passwords)
                    List<CtLiteral<?>> literals = spoon.getModel().getElements(new TypeFilter<>(CtLiteral.class));
                    for (CtLiteral<?> lit : literals) {
                        if (lit.getValue() instanceof String) {
                            String val = (String) lit.getValue();
                            String varName = getContainerName(lit);

                            // Detectar 16 dígitos (tarjetas) o nombres de variables sospechosos
                            if (val.matches(".*\\d{16}.*") || varName.contains("password") || varName.contains("secret") || varName.contains("key") || varName.contains("token")) {
                                diagnostics.add(new Diagnostic(
                                    createLiteralRange(lit.getPosition()),
                                    "SEGURIDAD: Posible dato sensible hardcoded (clave/token/tarjeta).",
                                    DiagnosticSeverity.Error, "SpoonSecurity"
                                ));
                            }
                        }
                    }

                    client.publishDiagnostics(new PublishDiagnosticsParams(uri, diagnostics));

                } catch (Exception e) {
                    System.err.println("Error en el análisis de Aldo: " + e.getMessage());
                }
            }

            private String getContainerName(CtLiteral<?> lit) {
                spoon.reflect.declaration.CtElement p = lit.getParent();
                if (p instanceof CtVariable) return ((CtVariable<?>) p).getSimpleName().toLowerCase();
                if (p instanceof CtAssignment) return ((CtAssignment<?, ?>) p).getAssigned().toString().toLowerCase();
                return "";
            }

            private Range createRange(SourcePosition pos, int length) {
                return new Range(new Position(pos.getLine() - 1, 0), new Position(pos.getLine() - 1, length));
            }

            private Range createLiteralRange(SourcePosition pos) {
                return new Range(
                    new Position(pos.getLine() - 1, pos.getColumn() - 1),
                    new Position(pos.getEndLine() - 1, pos.getEndColumn())
                );
            }

            private int calculateMaxLoopDepth(spoon.reflect.declaration.CtElement element) {
                int max = 0;
                List<CtLoop> loops = element.getElements(new TypeFilter<>(CtLoop.class));
                for (CtLoop loop : loops) {
                    int depth = 1 + calculateMaxLoopDepth(loop.getBody());
                    if (depth > max) max = depth;
                }
                return max;
            }

            private boolean hasAuditableAnnotation(CtMethod<?> method) {
                return method.getAnnotations().stream()
                    .anyMatch(a -> a.getAnnotationType().getSimpleName().equals("Auditable"));
            }

            @Override public CompletableFuture<Hover> hover(HoverParams params) { return CompletableFuture.completedFuture(null); }
        };
    }

    @Override public void connect(LanguageClient client) { this.client = client; }
    @Override public CompletableFuture<Object> shutdown() { return CompletableFuture.completedFuture(null); }
    @Override public void exit() {}
    @Override public WorkspaceService getWorkspaceService() { return new WorkspaceService() {
        @Override public void didChangeConfiguration(DidChangeConfigurationParams p) {}
        @Override public void didChangeWatchedFiles(DidChangeWatchedFilesParams p) {}
    };}
}
"""

try:
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"✅ Archivo corregido con éxito en: {path}")
except Exception as e:
    print(f"❌ Error al escribir el archivo: {e}")
