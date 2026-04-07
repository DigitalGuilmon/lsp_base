package com.lsp.spoon;

import org.eclipse.lsp4j.jsonrpc.Launcher;
import org.eclipse.lsp4j.launch.LSPLauncher;
import org.eclipse.lsp4j.services.LanguageClient;
import java.util.concurrent.ExecutionException;

public class SpoonLspLauncher {
    public static void main(String[] args) {
        try {
            SpoonLanguageServer server = new SpoonLanguageServer();
            Launcher<LanguageClient> l = LSPLauncher.createServerLauncher(server, System.in, System.out);
            server.connect(l.getRemoteProxy());
            l.startListening().get();
        } catch (Exception e) {
            System.err.println("Error en el servidor: " + e.getMessage());
        }
    }
}
