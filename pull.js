import shell from 'shelljs';
import chalk from "chalk";
import ora from "ora";

if (!shell.which('git')) {
    shell.echo('Sorry, this script requires git');
    shell.exit(1);
}

while (true) {
    console.log(chalk.blue("Pulling from main..."));
    shell.exec("git pull origin main")

    console.log(chalk.blue("Adding upstream..."));
    shell.exec("git remote add upstream https://github.com/raymondwang0225/AtomPunks")

    console.log(chalk.blue("Fetching upstream..."));
    shell.exec("git fetch upstream")

    console.log(chalk.blue("Merging upstream..."));
    shell.exec("git merge upstream/main")

    console.log(chalk.blue("Pushing to main..."));
    shell.exec("git push origin main")

    const spinner = ora('Waiting...').start();
    await new Promise(r => setTimeout(r, 60 * 1000));
    spinner.stop();
    console.log("\n===============================\n");
}
