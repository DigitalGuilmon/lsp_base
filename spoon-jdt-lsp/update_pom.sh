sed -i '' '/<\/dependencies>/a \
    <build> \
        <plugins> \
            <plugin> \
                <artifactId>maven-assembly-plugin</artifactId> \
                <configuration> \
                    <archive> \
                        <manifest> \
                            <mainClass>com.lsp.spoon.SpoonLspLauncher</mainClass> \
                        </manifest> \
                    </archive> \
                    <descriptorRefs> \
                        <descriptorRef>jar-with-dependencies</descriptorRef> \
                    </descriptorRefs> \
                </configuration> \
                <executions> \
                    <execution> \
                        <id>make-assembly</id> \
                        <phase>package</phase> \
                        <goals> <goal>single</goal> </goals> \
                    </execution> \
                </executions> \
            </plugin> \
        </plugins> \
    </build>' pom.xml
