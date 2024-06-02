import { NgIf } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  computed,
  forwardRef,
  input,
  OnInit, signal,
  ViewChild,
} from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { FormControl, NG_VALUE_ACCESSOR, ReactiveFormsModule } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import {
  combineLatest, distinctUntilChanged, filter, map,
} from 'rxjs';
import { shareReplay, startWith } from 'rxjs/operators';
import { buildNormalizedFileSize } from 'app/helpers/file-size.utils';
import { helptextVolumeStatus } from 'app/helptext/storage/volumes/volume-status';
import { Option } from 'app/interfaces/option.interface';
import { UnusedDisk } from 'app/interfaces/storage.interface';
import { DialogService } from 'app/modules/dialog/dialog.service';
import { SimpleAsyncComboboxProvider } from 'app/modules/ix-forms/classes/simple-async-combobox-provider';
import { IxComboboxComponent } from 'app/modules/ix-forms/components/ix-combobox/ix-combobox.component';
import { IxFormsModule } from 'app/modules/ix-forms/ix-forms.module';
import {
  getNonUniqueSerialDisksWarning,
} from 'app/pages/storage/modules/pool-manager/components/pool-manager-wizard/components/pool-warnings/get-non-unique-serial-disks';
import { hasNonUniqueSerial } from 'app/pages/storage/modules/pool-manager/utils/disk.utils';
import { WebSocketService } from 'app/services/ws.service';

/**
 * Presents unused disks, shows their size and if there is exported pool on them.
 * Shows warning when user selects a disk with an exported pool.
 * Show extra "Allow non-unique serialed disks" if user has such disks.
 */
@UntilDestroy()
@Component({
  selector: 'ix-unused-disk-select',
  templateUrl: './unused-disk-select.component.html',
  standalone: true,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => UnusedDiskSelectComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    IxFormsModule,
    ReactiveFormsModule,
    TranslateModule,
    NgIf,
  ],
})
export class UnusedDiskSelectComponent implements OnInit, AfterViewInit {
  /**
   * Optional function to filter disks in addition to default select's behaviour.
   */
  readonly diskFilteringFn = input<(disk: UnusedDisk) => boolean>();
  readonly label = input<string>();
  readonly required = input<boolean>();
  readonly tooltip = input<string>();
  // TODO: It may be better to allow for object to be written as value.
  readonly valueField = input<keyof UnusedDisk>('name');

  readonly unusedDisks = signal<UnusedDisk[]>([]);
  readonly nonUniqueSerialDisks = computed(() => this.unusedDisks().filter(hasNonUniqueSerial));

  readonly nonUniqueSerialDisksTooltip = computed(() => {
    return getNonUniqueSerialDisksWarning(this.nonUniqueSerialDisks(), this.translate);
  });

  private unusedDisks$ = this.ws.call('disk.get_unused').pipe(shareReplay({ bufferSize: 1, refCount: true }));

  protected allowDuplicateSerials = new FormControl(false);

  protected shownOptions$ = combineLatest([
    this.unusedDisks$,
    this.allowDuplicateSerials.valueChanges.pipe(startWith(false)),
    toObservable(this.diskFilteringFn),
    toObservable(this.valueField),
  ])
    .pipe(
      map(([unusedDisks, allowDuplicateSerials, filteringFn, valueField]) => {
        const disks = this.filterShownDisks(unusedDisks, { allowDuplicateSerials, filteringFn });
        return this.mapDisksToOptions(disks, valueField);
      }),
    );

  protected disksProvider = new SimpleAsyncComboboxProvider(this.shownOptions$);

  @ViewChild(IxComboboxComponent) private combobox: IxComboboxComponent;

  constructor(
    private dialogService: DialogService,
    private translate: TranslateService,
    private ws: WebSocketService,
  ) {}

  ngOnInit(): void {
    this.loadDisks();
  }

  ngAfterViewInit(): void {
    this.setupExportedPoolWarning();
  }

  private loadDisks(): void {
    this.unusedDisks$
      .pipe(untilDestroyed(this))
      .subscribe((disks) => {
        this.unusedDisks.set(disks);
      });
  }

  private setupExportedPoolWarning(): void {
    if (!this.combobox) {
      return;
    }
    this.combobox.controlDirective.control.valueChanges.pipe(
      distinctUntilChanged(),
      filter(Boolean),
      untilDestroyed(this),
    )
      .subscribe((diskName: string) => this.warnAboutExportedPool(diskName));
  }

  private filterShownDisks(
    unusedDisks: UnusedDisk[],
    {
      allowDuplicateSerials,
      filteringFn,
    }: {
      allowDuplicateSerials: boolean;
      filteringFn: (disk: UnusedDisk) => boolean;
    },
  ): UnusedDisk[] {
    return unusedDisks.filter((disk) => {
      if (hasNonUniqueSerial(disk) && !allowDuplicateSerials) {
        return false;
      }

      return filteringFn ? filteringFn(disk) : true;
    });
  }

  private mapDisksToOptions(unusedDisks: UnusedDisk[], valueField: keyof UnusedDisk): Option[] {
    return unusedDisks
      .map((disk) => {
        const exportedPool = disk.exported_zpool ? `(${disk.exported_zpool})` : '';

        return {
          label: `${disk.devname} (${buildNormalizedFileSize(disk.size)}) ${exportedPool}`,
          value: disk[valueField] as string,
        };
      })
      .sort((a, b) => a.label.localeCompare(b.label));
  }

  private warnAboutExportedPool(diskName: string): void {
    const unusedDisk = this.unusedDisks().find((disk) => disk.name === diskName);
    if (!unusedDisk?.exported_zpool) {
      return;
    }
    this.dialogService.warn(
      this.translate.instant('Warning') + ': ' + unusedDisk.name,
      this.translate.instant(helptextVolumeStatus.exported_pool_warning, { pool: `'${unusedDisk.exported_zpool}'` }),
    );
  }
}
