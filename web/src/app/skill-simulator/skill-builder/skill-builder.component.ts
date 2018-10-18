import {ChangeDetectionStrategy, ChangeDetectorRef, Component, ElementRef, OnDestroy, OnInit} from '@angular/core';
import {TOSJob} from "../../shared/domain/tos/job/tos-job.model";
import {Subscription} from "rxjs";
import {TOSEntity} from "../../shared/domain/tos/entity/tos-entity.model";
import {TOSSimulatorBuild} from "../../shared/domain/tos/tos-build";
import {ActivatedRoute, Params, Router} from "@angular/router";
import {faImage, faLink} from "@fortawesome/free-solid-svg-icons";
import {TosNeetService} from "../../shared/service/integrations/tos-neet.service";
import {TinyUrlService} from "../../shared/service/integrations/tiny-url.service";
import {ClipboardService} from "../../shared/service/clipboard.service";
import {TOSSkillRepository} from "../../shared/domain/tos/skill/tos-skill.repository";
import {TOSJobRepository} from "../../shared/domain/tos/job/tos-job.repository";

const PARAM_BUILD = 'build';
const PARAM_TINYURL = 'tinyurl';
const PARAM_TOSNEET = 'tosneet';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-builder',
  templateUrl: './skill-builder.component.html',
  styleUrls: ['./skill-builder.component.scss']
})
export class SkillBuilderComponent implements OnDestroy, OnInit {

  faImage = faImage;
  faLink = faLink;

  build: TOSSimulatorBuild = new TOSSimulatorBuild();
  buildChanged: boolean;
  jobs: TOSJob[];

  sharingAsImage: boolean;
  sharingAsUrl: boolean;
  tinyUrl: string;

  tooltip: TOSEntity;

  subscriptionBuild: Subscription;
  subscriptionQueryParams: Subscription;
  subscriptionJobs: Subscription;
  subscriptionTooltip: Subscription;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private clipboardService: ClipboardService,
    private element: ElementRef,
    private route: ActivatedRoute,
    private router: Router,
    private tinyUrlService: TinyUrlService,
    private tosNeetService: TosNeetService,
  ) {}

  private buildSubscribe() {
    this.subscriptionBuild && this.subscriptionBuild.unsubscribe();
    this.subscriptionJobs && this.subscriptionJobs.unsubscribe();
    this.subscriptionTooltip && this.subscriptionTooltip.unsubscribe();

    this.subscriptionBuild = this.build.Change.subscribe(value => this.onBuildChange());
    this.subscriptionJobs = this.build.Jobs.subscribe(value => this.onJobsChange(value));
    this.subscriptionTooltip = this.build.Tooltip.subscribe(value => this.tooltip = value);
  }

  shareAsImage() {
    let element = this.element.nativeElement as Element;
    let options = {
      backgroundColor: window.getComputedStyle(document.body).backgroundColor,
      foreignObjectRendering: false,
      ignoreElements: (element: Element) => ['button', 'fa-icon'].indexOf(element.tagName.toLowerCase()) > -1,
      logging: false,
      windowWidth: 1920,
    };

    // Configure ultra-wide design
    this.element.nativeElement.style.display = 'block';
    this.element.nativeElement.style.maxWidth = '1750px';
    this.element.nativeElement.style.width = '1750px';
    this.sharingAsImage = true;

    window['html2canvas'](element, options).then(canvas => {
      let a = document.createElement("a");
          a.href = canvas.toDataURL("image/png");
          a.download = 'build.png';
          a.click();

      // Revert ultra-wide design
      this.element.nativeElement.style.display = '';
      this.element.nativeElement.style.maxWidth = '';
      this.element.nativeElement.style.width = '';

      this.sharingAsImage = false;
      this.changeDetector.detectChanges();
    });
  }

  shareAsUrl() {
    if (this.tinyUrl) {
      this.clipboardService.write(this.tinyUrl);
      return;
    }

    let urlBase = location.protocol + '//' + location.host + location.pathname;
    let url = urlBase + '?' + PARAM_BUILD + '=' + TOSSimulatorBuild.base64Encode(this.build);

    this.tinyUrl = null;
    this.sharingAsUrl = true;

    this.tinyUrlService
      .create(url)
      .subscribe(value => {
        this.tinyUrl = urlBase + '?' + PARAM_TINYURL + '=' + value;
        this.sharingAsUrl = false;

        this.changeDetector.detectChanges();
      })
  }

  onBuildChange() {
    this.buildChanged = true;

    let queryParams = {};
        queryParams[PARAM_BUILD] = TOSSimulatorBuild.base64Encode(this.build);

    this.router.navigate(['.'], { queryParams, relativeTo: this.route });
  }

  onQueryParamsChange(value: Params) {
    if (this.buildChanged) {
      this.buildChanged = false;
      this.tinyUrl = null;
      return;
    }


    if (value[PARAM_TOSNEET]) {
      this.build = this.tosNeetService.decode(value[PARAM_TOSNEET]);
      this.buildSubscribe();
    } else if (value[PARAM_TINYURL]) {
      this.tinyUrlService
        .parse(value[PARAM_TINYURL])
        .subscribe(url => {
          let queryParams = {};
              queryParams[PARAM_BUILD] = url.split('?' + PARAM_BUILD + '=')[1];

          this.router.navigate(['.'], { queryParams, relativeTo: this.route });
        });
    } else if (value[PARAM_BUILD]) {
      this.build = TOSSimulatorBuild.base64Decode(value[PARAM_BUILD]);
      this.buildSubscribe();
    } else {
      this.build = new TOSSimulatorBuild();
      this.buildSubscribe();
    }

    this.changeDetector.detectChanges();
  }

  onJobsChange(jobs: TOSJob[]) {
    let unique = [];

    for (let job of jobs)
      if (unique.indexOf(job) == -1)
        unique.push(job);

    this.jobs = unique;
  }

  ngOnInit() {
    this.subscriptionQueryParams = this.route.queryParams.subscribe(value => this.onQueryParamsChange(value));
    this.buildSubscribe();
  }

  ngOnDestroy(): void {
    this.subscriptionBuild && this.subscriptionBuild.unsubscribe();
    this.subscriptionQueryParams && this.subscriptionQueryParams.unsubscribe();
    this.subscriptionJobs && this.subscriptionJobs.unsubscribe();
    this.subscriptionTooltip && this.subscriptionTooltip.unsubscribe();
  }

}