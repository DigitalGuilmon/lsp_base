package com.lsp.spoon;

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
import spoon.reflect.visitor.Filter;
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

                    // Escanear métodos
                    List<CtMethod<?>> methods = spoon.getModel().getElements(new Filter<CtMethod<?>>() {
                        @Override public boolean matches(CtMethod<?> m) { return true; }
                    });

                    for (CtMethod<?> method : methods) {
                        int maxDepth = calculateMaxLoopDepth(method);
                        boolean isAuditable = hasAuditableAnnotation(method);

                        // Regla: > 2 niveles y sin @Auditable
                        if (maxDepth > 2 && !isAuditable) {
                            SourcePosition pos = method.getPosition();
                            Range range = new Range(
                                new Position(pos.getLine() - 1, 0),
                                new Position(pos.getLine() - 1, method.getSimpleName().length() + 10)
                            );

                            // AQUÍ ESTÁ TU SALUDO PERSONALIZADO
                            String msg = "Hola Raul y Ajolote!!! de parte de Aldo!!! " +
                                         "CRÍTICO: Método con " + maxDepth + " niveles de anidación sin @Auditable.";

                            Diagnostic d = new Diagnostic(range, msg, DiagnosticSeverity.Error, "SpoonLinter");
                            diagnostics.add(d);
                        }
                    }

                    client.publishDiagnostics(new PublishDiagnosticsParams(uri, diagnostics));

                } catch (Exception e) {
                    System.err.println("Error en el análisis de Aldo: " + e.getMessage());
                }
            }

            private int calculateMaxLoopDepth(CtElement element) {
                int max = 0;
                List<CtLoop> loops = element.getElements(new Filter<CtLoop>() {
                    @Override public boolean matches(CtLoop l) { return true; }
                });
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
